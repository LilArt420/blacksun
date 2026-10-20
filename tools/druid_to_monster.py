# Makes a monster sprite out of a player body sprite (the Druid's werewolf or
# wereraptor form), so the beast is a real monster on the client: clicked to
# attack, a target for skills, and not mistaken for a player.
#
# A monster's .act has 5 actions per direction (stand, walk, attack, hurt,
# die); a player body's has 13 or more (stand, walk, sit, pick up, ready,
# attack, hurt, freeze, dead, ...). This keeps the player's stand, walk,
# attack and hurt, and makes the death out of the hurt frames followed by the
# crouch (a shapeshift's own "dead" is empty: a fallen Druid is human again).
# Every layer can be scaled and tinted. The .spr is unchanged.
#
#   python3 druid_to_monster.py <body.act> <out.act> [scale] [r,g,b multiplier 0..1]
# e.g. werewolf_남.act bs_james_wolf.act 1.35 0.45,0.4,0.48
import struct, sys

KEEP = ((0,), (1,), (5,), (6,), (6, 2))   # stand, walk, attack, hurt, die = hurt + crouch

src = open(sys.argv[1], 'rb').read()
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
tint = tuple(float(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (1.0, 1.0, 1.0)

assert src[:2] == b'AC', 'not an .act'
ver = struct.unpack_from('<H', src, 2)[0]
assert ver == 0x205, 'only .act 2.5 is handled, this is %x' % ver
count = struct.unpack_from('<H', src, 4)[0]
assert count % 8 == 0 and count // 8 > max(max(k) for k in KEEP), 'unexpected action count %d' % count

pos = 16
actions = []
for a in range(count):
    frames = []
    nframes = struct.unpack_from('<I', src, pos)[0]
    pos += 4
    for f in range(nframes):
        out = bytearray()
        out += src[pos:pos + 32]; pos += 32          # the two (unused) ranges
        nlayers = struct.unpack_from('<I', src, pos)[0]
        out += src[pos:pos + 4]; pos += 4
        for l in range(nlayers):
            x, y, spr, mirror = struct.unpack_from('<iiii', src, pos)
            r, g, b, al = struct.unpack_from('<BBBB', src, pos + 16)
            sx, sy = struct.unpack_from('<ff', src, pos + 20)
            angle, stype, w, h = struct.unpack_from('<iiii', src, pos + 28)
            out += struct.pack('<iiii', round(x * scale), round(y * scale), spr, mirror)
            out += struct.pack('<BBBB', round(r * tint[0]), round(g * tint[1]), round(b * tint[2]), al)
            out += struct.pack('<ff', sx * scale, sy * scale)
            out += struct.pack('<iiii', angle, stype, w, h)
            pos += 44
        out += src[pos:pos + 4]; pos += 4            # sound event
        nanch = struct.unpack_from('<I', src, pos)[0]
        out += src[pos:pos + 4]; pos += 4
        for k in range(nanch):
            u, ax, ay, attr = struct.unpack_from('<iiii', src, pos)
            out += struct.pack('<iiii', u, round(ax * scale), round(ay * scale), attr)
            pos += 16
        frames.append(bytes(out))
    actions.append(frames)

nevents = struct.unpack_from('<I', src, pos)[0]
events = src[pos:pos + 4 + 40 * nevents]; pos += 4 + 40 * nevents
delays = struct.unpack_from('<%df' % count, src, pos); pos += 4 * count
assert pos == len(src), 'trailing bytes: %d' % (len(src) - pos)

dst = bytearray(b'AC' + struct.pack('<HH', ver, 8 * len(KEEP)) + bytes(10))
order = []
for groups in KEEP:
    for d in range(8):
        frames = [f for g in groups for f in actions[g * 8 + d]]
        dst += struct.pack('<I', len(frames)) + b''.join(frames)
        order.append(groups[0] * 8 + d)
dst += events
dst += struct.pack('<%df' % len(order), *(delays[i] for i in order))
open(sys.argv[2], 'wb').write(dst)
print(sys.argv[2], len(order), 'actions, scale', scale, 'tint', tint)
