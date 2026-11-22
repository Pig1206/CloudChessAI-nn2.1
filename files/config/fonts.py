from PIL import ImageFont
import os

from files.config.paths_parameters import font_path as __fa

#字体初始化
__prf, __prz, __prh = ImageFont.truetype(os.path.join(__fa,'simfang.ttf')), \
                ImageFont.truetype(os.path.join(__fa,'simzhong.TTF')), \
                ImageFont.truetype(os.path.join(__fa,'simhei.ttf'))
pf, pz, ph = __prf.getname()[0], __prz.getname()[0], __prh.getname()[0]
