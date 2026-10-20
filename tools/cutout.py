# Turns a portrait on a flat background into a cut-in: the background made
# transparent from the edges inwards (only background that touches the border,
# so white clothes and highlights -- or black fur -- stay), enclosed gaps of the
# same flat colour too, and the figure's rim softened. The result keeps the
# picture's own size; tools/fit_portrait.py then frames it like Nightwing's.
#
#   python3 cutout.py <in.png> <out.png> [white|black|R,G,B]    (default white)
import sys
from collections import deque
from PIL import Image, ImageFilter

src = Image.open(sys.argv[1]).convert('RGB')
W, H = src.size
px = src.load()
bgarg = sys.argv[3] if len(sys.argv) > 3 else 'white'

if bgarg == 'white':
    def bgness(p):
        # 0 for anything with colour or shade, up to 1 for pure white
        lo = min(p)
        spread = max(p) - lo
        return max(0.0, min(1.0, (lo - 200) / 45)) * max(0.0, 1 - spread / 40)
    def flat(p):
        return min(p) >= 244 and max(p) - min(p) <= 8
elif bgarg == 'black':
    def bgness(p):
        # 1 for the background's black, 0 from the darkest fur up
        return max(0.0, min(1.0, (20 - max(p)) / 10))
    def flat(p):
        return max(p) <= 6
else:
    key = tuple(int(v) for v in bgarg.split(','))
    def bgness(p):
        d = sum(abs(a - b) for a, b in zip(p, key))
        return max(0.0, min(1.0, (40 - d) / 30))
    def flat(p):
        return sum(abs(a - b) for a, b in zip(p, key)) <= 6

bg = bytearray(W * H)          # 1 = background
q = deque()
for x in range(W):
    for y in (0, H - 1):
        q.append((x, y))
for y in range(H):
    for x in (0, W - 1):
        q.append((x, y))
while q:
    x, y = q.popleft()
    i = y * W + x
    if bg[i] or bgness(px[x, y]) < 0.5:
        continue
    bg[i] = 1
    if x > 0: q.append((x - 1, y))
    if x < W - 1: q.append((x + 1, y))
    if y > 0: q.append((x, y - 1))
    if y < H - 1: q.append((x, y + 1))

# enclosed gaps (between hair strands, under an arm, between legs) are
# background too when they are the flat background colour and large enough
seen = bytearray(W * H)
for sy in range(H):
    for sx in range(W):
        i0 = sy * W + sx
        if bg[i0] or seen[i0] or not flat(px[sx, sy]):
            continue
        comp = []; q = deque([(sx, sy)]); seen[i0] = 1
        while q:
            x, y = q.popleft(); comp.append(y * W + x)
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < W and 0 <= ny < H:
                    j = ny * W + nx
                    if not seen[j] and not bg[j] and flat(px[nx, ny]):
                        seen[j] = 1; q.append((nx, ny))
        if len(comp) >= 120:
            for j in comp: bg[j] = 1

alpha = Image.new('L', (W, H))
a = alpha.load()
for y in range(H):
    for x in range(W):
        a[x, y] = 0 if bg[y * W + x] else 255
# a soft rim: pixels next to the background take part of its transparency
edge = alpha.filter(ImageFilter.MinFilter(3))
rim = alpha.filter(ImageFilter.GaussianBlur(1.0))
r = rim.load(); e = edge.load()
for y in range(H):
    for x in range(W):
        if a[x, y] and not e[x, y]:
            # on the rim: keep what isn't background
            a[x, y] = int(min(r[x, y], 255 * (1 - 0.8 * bgness(px[x, y]))))
out = src.convert('RGBA')
out.putalpha(alpha)
out.save(sys.argv[2], format='PNG')
print(sys.argv[2], out.size)
