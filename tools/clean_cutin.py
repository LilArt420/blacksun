# Cleans a cut-out portrait's edges, the leftovers of the background it was
# cut from:
#  - holes: transparent specks inside the figure (up to <max hole> pixels, not
#    joined to the outside) are filled back in;
#  - the halo: the rim pixels still carry some of the old background's colour,
#    a pale line on a dark scene. Every pixel within 2 of the outline takes the
#    colour of the figure just inside it instead, so white bandages and fur
#    stay white and dark hair stops glowing at its edge.
#   python3 clean_cutin.py <in.png> <out.png> [max hole px, default 40]
import sys
from collections import deque
from PIL import Image, ImageChops, ImageFilter

MAXHOLE = int(sys.argv[3]) if len(sys.argv) > 3 else 40

im = Image.open(sys.argv[1]).convert('RGBA')
W, H = im.size
r, g, b, a = im.split()

# holes
ap = a.load()
seen = bytearray(W * H)
fill = set()
for sy in range(H):
    for sx in range(W):
        if seen[sy * W + sx] or ap[sx, sy] >= 128:
            continue
        comp = []; q = deque([(sx, sy)]); seen[sy * W + sx] = 1; outside = False
        while q:
            x, y = q.popleft(); comp.append((x, y))
            if x in (0, W - 1) or y in (0, H - 1):
                outside = True
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and ap[nx, ny] < 128:
                    seen[ny * W + nx] = 1; q.append((nx, ny))
        if not outside and len(comp) <= MAXHOLE:
            # the hole and its soft rim (2 px), which was cut out with it
            for x, y in comp:
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if 0 <= x + dx < W and 0 <= y + dy < H and ap[x + dx, y + dy] < 255:
                            ap[x + dx, y + dy] = 255
                            fill.add((x + dx, y + dy))
filled = Image.merge('RGBA', (r, g, b, a))

# the colour just inside the outline, spread outwards over the rim (and over
# the filled holes, whose own pixels may hold nothing)
inner = a.point(lambda v: 255 if v > 200 else 0).filter(ImageFilter.MinFilter(5))
ip = inner.load()
for x, y in fill:
    ip[x, y] = 0
rgb_in = ImageChops.multiply(filled.convert('RGB'), Image.merge('RGB', (inner, inner, inner)))
blur_rgb = rgb_in.filter(ImageFilter.GaussianBlur(2.5)).load()
blur_w = inner.filter(ImageFilter.GaussianBlur(2.5)).load()
px = filled.load(); inn = inner.load()
for y in range(H):
    for x in range(W):
        if not ap[x, y] or inn[x, y]:
            continue
        w = blur_w[x, y]
        if w < 8:
            continue
        cr, cg, cb = blur_rgb[x, y]
        px[x, y] = (min(255, cr * 255 // w), min(255, cg * 255 // w), min(255, cb * 255 // w), ap[x, y])
filled.save(sys.argv[2], format='PNG')
print(sys.argv[2], filled.size)
