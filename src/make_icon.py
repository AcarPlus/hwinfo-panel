"""Generates panel.ico / panel.png: a green-to-red gauge ring with a needle on a dark rounded square.
No extra packages needed (PNG through tkinter PhotoImage, ICO container written by hand)."""
import math, os, struct, tkinter as tk

HERE = os.path.dirname(os.path.abspath(__file__))
STOPS = [(0.0, (46, 160, 67)), (0.25, (124, 194, 66)), (0.5, (227, 179, 65)), (0.75, (240, 136, 62)),
         (1.0, (248, 81, 73))]
BG = (18, 24, 32)
NEEDLE = (240, 246, 252)


def grad(t):
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(a + (b - a) * f for a, b in zip(c0, c1))
    return STOPS[-1][1]


def sample(x, y):
    """One point in the unit square (0..1): (r, g, b, a) 0..255."""
    # rounded square
    r = 0.2
    dx, dy = max(abs(x - 0.5) - (0.5 - r), 0), max(abs(y - 0.5) - (0.5 - r), 0)
    if dx * dx + dy * dy > r * r:
        return (0, 0, 0, 0)
    cx, cy = x - 0.5, y - 0.53
    d = math.hypot(cx, cy)
    ang = math.degrees(math.atan2(-cy, cx))          # 0 = right, counter-clockwise
    sweep = (225 - ang) % 360                          # clockwise from 225 degrees
    # ring: 270 degree arc
    if 0.27 <= d <= 0.37 and sweep <= 270:
        return (*grad(sweep / 270), 255)
    # needle: points at ~70% of the scale
    na = math.radians(225 - 270 * 0.70)
    ux, uy = math.cos(na), -math.sin(na)
    proj = cx * ux + cy * uy
    perp = abs(cx * uy - cy * ux)
    if -0.02 <= proj <= 0.30 and perp <= 0.035 * (1 - proj / 0.36):
        return (*NEEDLE, 255)
    if d <= 0.065:
        return (*NEEDLE, 255)
    return (*BG, 255)


def render(size, ss=3):
    rows = []
    for py in range(size):
        row = []
        for px in range(size):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = sample((px + (sx + 0.5) / ss) / size, (py + (sy + 0.5) / ss) / size)
                    a = c[3]
                    acc[0] += c[0] * a; acc[1] += c[1] * a; acc[2] += c[2] * a; acc[3] += a
            n = ss * ss
            a = acc[3] / n
            if a == 0:
                row.append((0, 0, 0, 0))
            else:
                row.append((round(acc[0] / acc[3]), round(acc[1] / acc[3]), round(acc[2] / acc[3]), round(a)))
        rows.append(row)
    return rows


def to_png(rows, path, root):
    size = len(rows)
    img = tk.PhotoImage(master=root, width=size, height=size)
    for y, row in enumerate(rows):
        img.put("{" + " ".join("#%02x%02x%02x" % p[:3] for p in row) + "}", to=(0, y))
        for x, p in enumerate(row):
            if p[3] < 255:
                img.transparency_set(x, y, p[3] < 128)
    img.write(path, format="png")


def main():
    root = tk.Tk(); root.withdraw()
    sizes = [16, 24, 32, 48, 64, 256]
    blobs = []
    for s in sizes:
        tmp = os.path.join(HERE, f"_icon{s}.png")
        to_png(render(s), tmp, root)
        blobs.append(open(tmp, "rb").read())
        os.remove(tmp)
    to_png(render(256), os.path.join(HERE, "panel.png"), root)
    hdr = struct.pack("<HHH", 0, 1, len(sizes))
    off = 6 + 16 * len(sizes)
    ent, data = b"", b""
    for s, b in zip(sizes, blobs):
        ent += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(b), off + len(data))
        data += b
    open(os.path.join(HERE, "panel.ico"), "wb").write(hdr + ent + data)
    print("panel.ico written")


if __name__ == "__main__":
    main()
