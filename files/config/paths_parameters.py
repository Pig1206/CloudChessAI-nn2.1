import os

__f = os.path.dirname(os.path.abspath(__file__))
__uf = os.path.dirname(__f)

config_path = os.path.join(__uf,'config')

font_path = os.path.join(__f,'fonts')

data_path = os.path.join(__uf,'data')

network_path = os.path.join(__uf,'network')

functions_path = os.path.join(__uf,'functions')

ui_path = os.path.join(__uf,'ui')

images_path = os.path.join(os.path.dirname(__uf),'images')

files_path = os.path.join(os.path.dirname(__uf),'files')