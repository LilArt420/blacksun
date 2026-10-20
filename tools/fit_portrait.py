# Fits a portrait to Nightwing's cut-in frame: 852 x 691, transparent,
# the figure scaled so it fills the height the way his does, centred on its
# own bounding box, the bottom of the frame cutting it at the waist.
# Saves PNG data under the given name (.bmp is fine: the client reads by content).
#   python3 fit_portrait.py <in.png> <out.bmp>
import sys
from PIL import Image

W, H = 852, 691
TOP = 8          # gap above the head, as in rn_nightwing.bmp

src = Image.open(sys.argv[1]).convert('RGBA')
box = src.getbbox()           # the figure, without the empty border
if box is None:
    sys.exit('the image is empty')
fig = src.crop(box)
# as tall as the frame (head to waist), or as wide, whichever fits first
scale = min((H - TOP) / fig.height * 1.0, W / fig.width)
# a full-length figure: keep it waist-up by letting it run off the bottom
if fig.height / fig.width > 1.6:
    scale = (H - TOP) / (fig.height * 0.62)
fig = fig.resize((max(1, round(fig.width * scale)), max(1, round(fig.height * scale))), Image.LANCZOS)
out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
out.paste(fig, ((W - fig.width) // 2, TOP), fig)
out.save(sys.argv[2], format='PNG')
print(f'{sys.argv[2]}: {W}x{H}, figure {fig.width}x{fig.height}')
