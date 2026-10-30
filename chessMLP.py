import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

print("加载已保存的数据...")
loaded_data = torch.load('p_merged.pt')
bos = loaded_data['boards']
mos = loaded_data['moves']
print(f"加载的数据: 棋局 {bos.shape}, 结果 {mos.shape}")

print(mos.shape, mos.dtype)
indices = torch.randperm(len(bos))
split = int(len(bos) * 0.93)
train_indices = indices[:split]
val_indices = indices[split:]
train_bos = bos[train_indices]
train_mos = mos[train_indices]
val_bos = bos[val_indices]
val_mos = mos[val_indices]
print(f"训练集: {len(train_bos)} 张, 验证集: {len(val_bos)} 张")

train_dataset = TensorDataset(train_bos, train_mos)
val_dataset = TensorDataset(val_bos, val_mos)
train_loader = DataLoader(train_dataset, batch_size=1024, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)


class ChessMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Dropout2d(0.2),

            nn.Conv2d(16, 32, kernel_size=5, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Dropout2d(0.25),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(0.2),

            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(0.1),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.1)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.60),

            nn.Linear(128, 121)
        )

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.conv(x)
        x = self.fc(x)
        return x


def evaluate_accuracy(model, data_loader, device):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    return correct / total if total > 0 else 0.0


def evaluate_top5(model, data_loader, device):
    model.eval()
    correct_top5 = 0
    total = 0

    with torch.no_grad():
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)

            top5_preds = torch.topk(outputs, 5, dim=1).indices
            labels_expanded = labels.unsqueeze(1)
            correct_top5 += (top5_preds == labels_expanded).any(dim=1).sum().item()
            total += labels.size(0)

    return correct_top5 / total if total > 0 else 0.0


def evaluate_loss(model, data_loader, device, criterion):
    model.eval()
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for images, labels in data_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            total_samples += images.size(0)

    return total_loss / total_samples if total_samples > 0 else 0.0


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"使用设备: {device}")
model = ChessMLP().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0005)

# 余弦退火
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=40, eta_min=1e-6)

checkpoint = torch.load('PN7-CPT120.pth')
start_epoch = 1
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
optimizer.param_groups[0]['lr'] = 0.00002
start_epoch = checkpoint['epoch'] + 1


def writein(name, text):
    f = open(name, 'a', encoding='utf-8')
    f.writelines('\n' + text)
    f.close()


print('Start')
Epoch = 1000

for epoch in range(start_epoch, Epoch + 1):
    # ========== 训练阶段 ==========
    model.train()
    running_loss = 0.0

    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        y_pred = model(X_batch)
        loss = criterion(y_pred, y_batch)
        running_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # ========== 计算训练集指标 ==========
    train_loss = running_loss / len(train_loader)
    train_acc = evaluate_accuracy(model, train_loader, device)
    train_top5 = evaluate_top5(model, train_loader, device)

    # ========== 计算验证集指标 ==========
    val_loss = evaluate_loss(model, val_loader, device, criterion)
    val_acc = evaluate_accuracy(model, val_loader, device)
    val_top5 = evaluate_top5(model, val_loader, device)

    # 调整学习率
    scheduler.step()

    # ========== 打印日志 ==========
    a = optimizer.param_groups[0]['lr']
    text = f'Epoch:{epoch:4d} | TrainLoss:{train_loss:.4f} | ValLoss:{val_loss:.4f} | TrainAcc:{train_acc:.2%} | ValAcc:{val_acc:.2%} | TrainTop5:{train_top5:.2%} | ValTop5:{val_top5:.2%} | LR:{a:.6f}'
    print(text)
    writein('logp.txt', text)

    # ========== 保存断点 ==========
    if epoch % 5 == 0 or epoch == Epoch:
        checkpoint = {
            'Name': 'CCS',
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_acc': train_acc,
            'val_acc': val_acc,
            'train_top5': train_top5,
            'val_top5': val_top5
        }
        torch.save(checkpoint, f'PN7-CPT{epoch}.pth')
        print(f'  断点保存: CCS-CPT{epoch}.pth')

print("\n训练完成！")