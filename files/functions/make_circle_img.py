from PIL import Image, ImageDraw

def make_circle_img(img_path, size=(80, 80)):
    try:
        im = Image.open(img_path).convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)

        # 创建圆形mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        # 应用mask
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result
    except:
        # 如果图片不存在，返回默认头像
        im = Image.new('RGBA', size, (200, 200, 200, 255))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result