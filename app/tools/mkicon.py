import os
from PIL import Image, ImageDraw

APP = os.environ.get("APP_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def gradient(size, a=(58,160,255), b=(255,94,138), c=(122,92,255)):
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        for_x = None
    # diagonal gradient via numpy-free loop on rows is slow; build small then upscale
    small = 256
    g = Image.new("RGB", (small, small))
    px = g.load()
    for y in range(small):
        for x in range(small):
            t = (x + y) / (2 * (small - 1))
            if t < 0.5:
                u = t / 0.5
                col = tuple(int(a[i] + (c[i] - a[i]) * u) for i in range(3))
            else:
                u = (t - 0.5) / 0.5
                col = tuple(int(c[i] + (b[i] - c[i]) * u) for i in range(3))
            px[x, y] = col
    return g.resize((size, size), Image.LANCZOS)

def glyph(d, S, cx, cy, w, col=(255, 255, 255, 255)):
    """Photo glyph: rounded frame, sun, mountain. w = stroke width."""
    half = w  # glyph box half-size
    x0, y0, x1, y1 = cx - half, cy - half, cx + half, cy + half
    r = half * 0.34
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=col, width=int(w * 0.075 + 0.5))
    sr = half * 0.155
    scx, scy = cx - half * 0.34, cy - half * 0.34
    d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=col)
    # mountain
    pts = [
        (x0 + half * 0.10, y1 - half * 0.16),
        (cx - half * 0.10, cy + half * 0.12),
        (cx + half * 0.14, cy + half * 0.40),
        (cx + half * 0.36, cy + half * 0.14),
        (x1 - half * 0.10, y1 - half * 0.16),
    ]
    d.line(pts, fill=col, width=int(w * 0.075 + 0.5), joint="curve")

legacy = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
fg = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}

for dens, s in legacy.items():
    SS = 4
    big = s * SS
    bg = gradient(big)
    mask = Image.new("L", (big, big), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, big - 1, big - 1], radius=int(big * 0.22), fill=255)
    icon = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    icon.paste(bg, (0, 0), mask)
    d = ImageDraw.Draw(icon)
    glyph(d, SS, big / 2, big / 2, big * 0.30, (255, 255, 255, 255))
    icon.resize((s, s), Image.LANCZOS).save(f"{APP}/res/mipmap-{dens}/ic_launcher.png")

for dens, s in fg.items():
    SS = 4
    big = s * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    glyph(d, SS, big / 2, big / 2, big * 0.22, (255, 255, 255, 255))
    img.resize((s, s), Image.LANCZOS).save(f"{APP}/res/mipmap-{dens}/ic_fg.png")

print("icons written")
