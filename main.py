#!/usr/bin/env python3
"""news-image-20261119 top-10 entry: 'Thursday 19 November 2026, one day, 17 stories'.

Renders a single 1024x1024 PNG with Python stdlib + PIL only, no network,
no web fonts. Deterministic: same input always produces the same bytes.
Writes assets/entry.png (beside this file) and $MAKEFUN_OUTPUT_DIR/entry.png
(default /output), byte-identical in both places.
"""
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
CREAM = (251, 247, 238)
INK = (0, 0, 0)
RED = (179, 21, 27)
SKY = (201, 220, 235)
SKYLINE = (110, 143, 176)
WOOD = (90, 58, 40)
NAVY = (31, 56, 100)
GREY = (107, 114, 128)
GREEN = (30, 122, 52)
BLUE = (31, 78, 121)
YELLOW = (255, 215, 0)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
COND_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"

_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def tw(f, s):
    return f.getbbox(s)[2]


def wrap_lines(f, text, max_w):
    """Greedy word wrap into lines no wider than max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(f, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_wrap(path, text, max_w, start, minimum, max_lines=2):
    """Largest size in [minimum, start] whose wrap fits in max_lines lines."""
    for size in range(start, minimum - 1, -1):
        f = font(path, size)
        lines = wrap_lines(f, text, max_w)
        if len(lines) <= max_lines:
            return f, lines, size
    f = font(path, minimum)
    return f, wrap_lines(f, text, max_w), minimum


def fit_single(path, text, max_w, start, minimum):
    """Largest size in [minimum, start] whose single line fits max_w."""
    for size in range(start, minimum - 1, -1):
        f = font(path, size)
        if tw(f, text) <= max_w:
            return f, size
    return font(path, minimum), minimum


def star_points(cx, cy, r_out, r_in, points=5):
    import math
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_tracked(d, cx, y, text, f, fill, tracking):
    """Draw text centered on cx with extra tracking between glyphs."""
    widths = [tw(f, ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=fill)
        x += w + tracking


# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    kicker = font(SANS_BOLD, 20)
    draw_tracked(d, W // 2, 14, "THE WORLD IN ONE DAY", kicker, INK, 6)
    date_f, _ = fit_single(SERIF_BOLD, "THURSDAY 19 NOVEMBER 2026", 998, 64, 48)
    d.text((W // 2, 44), "THURSDAY 19 NOVEMBER 2026", font=date_f,
           fill=INK, anchor="ma")
    d.rectangle([13, 122, 1011, 124], fill=INK)


# ---------------------------------------------------------------- hero scene
def draw_flag_us(d, x, y):
    # 5 bars + canton, 110x70
    for i, col in enumerate([RED, CREAM, RED, CREAM, RED]):
        d.rectangle([x, y + i * 14, x + 110, y + (i + 1) * 14], fill=col)
    d.rectangle([x, y, x + 44, y + 28], fill=NAVY)
    d.rectangle([x, y, x + 110, y + 70], outline=INK, width=2)


def draw_flag_cn(d, x, y):
    d.rectangle([x, y, x + 110, y + 70], fill=RED)
    # one large star + four small stars in an arc (China, not Vietnam)
    d.polygon(star_points(x + 35, y + 35, 10.5, 4.2), fill=YELLOW)
    for sx, sy in ((x + 70, y + 14), (x + 84, y + 28), (x + 84, y + 49),
                   (x + 70, y + 63)):
        d.polygon(star_points(sx, sy, 3.5, 1.4), fill=YELLOW)
    d.rectangle([x, y, x + 110, y + 70], outline=INK, width=2)


def draw_flag_ru(d, x, y):
    d.rectangle([x, y, x + 110, y + 23], fill=(255, 255, 255))
    d.rectangle([x, y + 23, x + 110, y + 47], fill=(0, 57, 166))
    d.rectangle([x, y + 47, x + 110, y + 70], fill=(213, 0, 50))
    d.rectangle([x, y, x + 110, y + 70], outline=INK, width=2)


def draw_hero(d):
    hx, hy, hw = 13, 128, 640
    # sky
    d.rectangle([hx, hy, hx + hw, hy + 280], fill=SKY)
    # skyline silhouette, base y=340
    buildings = [
        (20, 52, 96), (82, 44, 132), (136, 62, 78), (208, 48, 118),
        (266, 58, 88), (334, 46, 140), (390, 60, 96), (460, 50, 124),
        (520, 56, 84), (586, 54, 110),
    ]
    for bx, bw, bh in buildings:
        d.rectangle([hx + bx, 340 - bh, hx + bx + bw, 340], fill=SKYLINE)
    # antenna spikes on two buildings
    for ax in (hx + 104, hx + 357):
        d.line([ax, 340 - 132, ax, 340 - 156], fill=SKYLINE, width=3)
        d.ellipse([ax - 3, 340 - 162, ax + 3, 340 - 156], fill=SKYLINE)
    # ground band below the skyline
    d.rectangle([hx, 340, hx + hw, hy + 280], fill=(183, 201, 216))
    # flag poles
    for px in (83, 278, 473):
        d.line([px, 196, px, 390], fill=INK, width=3)
    # flags
    draw_flag_us(d, 83, 196)
    draw_flag_cn(d, 278, 196)
    draw_flag_ru(d, 473, 196)
    # faceless seated silhouettes (navy, red, grey) behind the table
    for cx, col in ((138, NAVY), (333, RED), (528, GREY)):
        d.ellipse([cx - 17, 293, cx + 17, 327], fill=col)
        d.ellipse([cx - 46, 336, cx + 46, 396], fill=col)
    # dark-wood oval table
    d.ellipse([73, 354, 593, 406], fill=WOOD, outline=INK, width=2)
    # white paper on the table
    d.rectangle([158, 362, 508, 394], fill=(255, 255, 255), outline=INK, width=1)
    paper_f = font(SANS_BOLD, 18)
    d.text((333, 378), "DECLARATION TOWARD PEACE", font=paper_f,
           fill=INK, anchor="mm")
    # black headline band
    d.rectangle([hx, 408, hx + hw, 508], fill=INK)
    head_f, _ = fit_single(COND_BOLD, "TRUMP, XI AND PUTIN", 616, 48, 40)
    # place the two lines from measured ink height so nothing clips
    # (anchor "mt": ink spans y .. y+ink_h, so y2 = y1 + ink_h + 8)
    bb = d.textbbox((0, 0), "TRUMP, XI AND PUTIN", font=head_f, anchor="mt")
    ink_h = bb[3] - bb[1]
    y1 = 414
    y2 = y1 + ink_h + 8
    if y2 + ink_h > 504:
        head_f, _ = fit_single(COND_BOLD, "TRUMP, XI AND PUTIN", 616, 44, 38)
        bb = d.textbbox((0, 0), "TRUMP, XI AND PUTIN", font=head_f, anchor="mt")
        ink_h = bb[3] - bb[1]
        y1 = 414
        y2 = y1 + ink_h + 8
    d.text((hx + hw // 2, y1), "TRUMP, XI AND PUTIN", font=head_f,
           fill=(255, 255, 255), anchor="mt")
    d.text((hx + hw // 2, y2), "MEET IN SHENZHEN", font=head_f,
           fill=(255, 255, 255), anchor="mt")
    # red date chip, top-left of hero
    d.rectangle([25, 140, 189, 180], fill=RED)
    chip_f = font(SANS_BOLD, 22)
    d.text((107, 160), "THU 19 NOV", font=chip_f, fill=(255, 255, 255),
           anchor="mm")


# ---------------------------------------------------------------- right cards
def draw_right_cards(d):
    # Card 2: GTA VI — black card, white text
    d.rectangle([667, 128, 1011, 314], fill=INK)
    f, lines, _ = fit_wrap(COND_BOLD, "GTA VI LAUNCHES WORLDWIDE", 312, 30, 24)
    y = 146
    for ln in lines:
        d.text((683, y), ln, font=f, fill=(255, 255, 255), anchor="la")
        y += 34
    num_f = font(COND_BOLD, 54)
    d.text((683, 226), "OUT NOW", font=num_f, fill=(255, 255, 255), anchor="la")
    # controller silhouette, bottom-right (kept clear of OUT NOW)
    d.rounded_rectangle([920, 246, 996, 290], radius=12,
                        outline=(255, 255, 255), width=2)
    d.ellipse([932, 260, 944, 272], outline=(255, 255, 255), width=2)
    d.ellipse([972, 260, 984, 272], outline=(255, 255, 255), width=2)
    d.rectangle([952, 264, 962, 268], fill=(255, 255, 255))
    # Card 3: Anthropic — cream card, black border
    d.rectangle([667, 322, 1011, 508], fill=CREAM, outline=INK, width=2)
    f, lines, _ = fit_wrap(COND_BOLD, "ANTHROPIC LISTS ON NASDAQ", 312, 30, 24)
    y = 338
    for ln in lines:
        d.text((683, y), ln, font=f, fill=INK, anchor="la")
        y += 34
    big_f, _ = fit_single(COND_BOLD, "$81.3B IPO", 312, 54, 40)
    d.text((683, 412), "$81.3B IPO", font=big_f, fill=INK, anchor="la")
    # green up arrow (drawn triangle) + ANT $83
    d.polygon([(683, 494), (695, 476), (707, 494)], fill=GREEN)
    sub_f = font(COND_BOLD, 24)
    d.text((714, 472), "ANT $83", font=sub_f, fill=GREEN, anchor="la")


# ---------------------------------------------------------------- mid grid
def icon_scales(d, ix, iy):
    d.line([ix + 42, iy + 8, ix + 42, iy + 68], fill=INK, width=4)
    d.line([ix + 10, iy + 18, ix + 74, iy + 18], fill=INK, width=4)
    for cx in (ix + 10, ix + 74):
        d.line([cx, iy + 18, cx - 8, iy + 44], fill=INK, width=3)
        d.line([cx, iy + 18, cx + 8, iy + 44], fill=INK, width=3)
        d.polygon([(cx - 9, iy + 44), (cx + 9, iy + 44), (cx, iy + 56)],
                  outline=INK, width=2)
    d.line([ix + 28, iy + 68, ix + 56, iy + 68], fill=INK, width=4)


def icon_target(d, ix, iy):
    d.rounded_rectangle([ix + 6, iy + 10, ix + 78, iy + 74], radius=8,
                        outline=INK, width=2)
    d.ellipse([ix + 20, iy + 20, ix + 64, iy + 64], outline=INK, width=3)
    d.ellipse([ix + 30, iy + 30, ix + 54, iy + 54], outline=INK, width=3)
    d.ellipse([ix + 39, iy + 39, ix + 45, iy + 45], fill=INK)


def icon_cyclone(d, ix, iy):
    # spiral swirl: staggered arcs, not full circles (must differ from target)
    cx, cy = ix + 42, iy + 42
    d.arc([cx - 30, cy - 30, cx + 30, cy + 30], 30, 300, fill=INK, width=3)
    d.arc([cx - 19, cy - 19, cx + 19, cy + 19], 150, 60, fill=INK, width=3)
    d.arc([cx - 9, cy - 9, cx + 9, cy + 9], 270, 180, fill=INK, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)


def icon_rain(d, ix, iy):
    d.ellipse([ix + 8, iy + 28, ix + 50, iy + 54], fill=INK)
    d.ellipse([ix + 30, iy + 16, ix + 70, iy + 48], fill=INK)
    d.rectangle([ix + 8, iy + 40, ix + 70, iy + 54], fill=INK)
    for dx in (20, 38, 56):
        d.line([ix + dx, iy + 60, ix + dx - 4, iy + 74], fill=INK, width=3)


def icon_exam(d, ix, iy):
    d.rectangle([ix + 16, iy + 8, ix + 60, iy + 76], outline=INK, width=2)
    for ly in (22, 34, 46):
        d.line([ix + 24, iy + ly, ix + 52, iy + ly], fill=INK, width=2)
    d.line([ix + 58, iy + 62, ix + 76, iy + 22], fill=INK, width=8)
    d.polygon([(ix + 76, iy + 22), (ix + 70, iy + 14), (ix + 80, iy + 14)],
              fill=INK)


def icon_bars(d, ix, iy):
    d.rectangle([ix + 12, iy + 44, ix + 28, iy + 70], fill=INK)
    d.rectangle([ix + 34, iy + 32, ix + 50, iy + 70], fill=INK)
    d.rectangle([ix + 56, iy + 18, ix + 72, iy + 70], fill=INK)
    d.line([ix + 8, iy + 70, ix + 76, iy + 70], fill=INK, width=3)


MID = [
    ("WORLD COURT: MYANMAR RESPONSIBLE FOR GENOCIDE", "REPORTED", icon_scales, INK),
    ("IRAN SAYS IT HIT US BASE, KUWAIT", "CLAIM", icon_target, RED),
    ("CYCLONE AKVAN NEARS INDIA", "FORECAST", icon_cyclone, BLUE),
    ("FLORIDA: 15 INCHES OF RAIN IN 24 HOURS", "REPORTED", icon_rain, INK),
    ("551,864 SIT THE SUNEUNG EXAM", "REPORTED", icon_exam, INK),
    ("AUSTRALIA JOBLESS RATE HITS 4.9%", "REPORTED", icon_bars, INK),
]

TAG_FILL = {"REPORTED": INK, "CLAIM": RED, "FORECAST": BLUE}


def _uniform_mid_size():
    """Largest size in [20..27] where EVERY MID headline wraps to <=3 lines
    at width 201 (per-headline largest fitting size, then the minimum)."""
    sizes = []
    for headline, _, _, _ in MID:
        s = 20
        for cand in range(27, 19, -1):
            if len(wrap_lines(font(COND_BOLD, cand), headline, 201)) <= 3:
                s = cand
                break
        sizes.append(s)
    return min(sizes)


MID_SIZE = _uniform_mid_size()


def draw_mid_grid(d):
    d.rectangle([13, 512, 1011, 516], fill=INK)
    xs = (13, 350, 687)
    ys = (520, 684)
    for i, (headline, tag, icon_fn, _) in enumerate(MID):
        x = xs[i % 3]
        y = ys[i // 3]
        d.rectangle([x, y, x + 323, y + 152], fill=CREAM, outline=INK, width=2)
        icon_fn(d, x + 14, y + 34)
        tx = x + 110
        f = font(COND_BOLD, MID_SIZE)
        lines = wrap_lines(f, headline, 201)
        size = MID_SIZE
        leading = size + 6
        block = len(lines) * leading + 8 + 22
        ty = y + (152 - block) // 2
        for ln in lines:
            d.text((tx, ty), ln, font=f, fill=INK, anchor="la")
            ty += leading
        ty += 8
        chip_f = font(COND_BOLD, 13)
        cw = tw(chip_f, tag) + 16
        d.rectangle([tx, ty, tx + cw, ty + 22], fill=TAG_FILL[tag])
        d.text((tx + cw // 2, ty + 11), tag, font=chip_f,
               fill=(255, 255, 255), anchor="mm")


# ---------------------------------------------------------------- strip + footer
STRIP = [
    "ISRAEL ENDS GAZA TANK RAID",
    "CRIMEAN BRIDGE HIT AGAIN",
    "DOW FALLS 561 POINTS",
    "COLOMBIA HOLDS NATIONAL STRIKE",
    "KENYA FLOODS KILL SIX",
    "VOYAGER 1: ONE LIGHT-DAY OUT",
    "EBOLA EMERGENCY KEPT",
    "COP31 ENTERS FINAL STRETCH",
]


def draw_strip(d):
    label_f = font(SANS_BOLD, 16)
    d.text((13, 848), "ALSO ON THURSDAY 19 NOVEMBER", font=label_f, fill=RED,
           anchor="la")
    xs = (13, 266, 519, 772)
    ys = (876, 932)
    for i, item in enumerate(STRIP):
        x = xs[i % 4]
        y = ys[i // 4]
        f, lines, _ = fit_wrap(COND_BOLD, item, 239, 24, 20)
        ty = y
        for ln in lines:
            d.text((x, ty), ln, font=f, fill=INK, anchor="la")
            ty += 28


def draw_footer(d):
    f = font(SANS_BOLD, 14)
    d.text((W // 2, 1006),
           "THU 19 NOV 2026 \u00b7 REPORTED = confirmed \u00b7 CLAIM = one side "
           "\u00b7 FORECAST = not yet happened",
           font=f, fill=INK, anchor="ma")


def render():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_hero(d)
    draw_right_cards(d)
    draw_mid_grid(d)
    draw_strip(d)
    draw_footer(d)
    return img


def main():
    img = render()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()

    root = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(root, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    repo_path = os.path.join(assets_dir, "entry.png")
    with open(repo_path, "wb") as fh:
        fh.write(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as fh:
        fh.write(data)

    print("repo: %s (%d bytes)" % (repo_path, len(data)))
    print("out:  %s (%d bytes)" % (out_path, len(data)))
    print("size: %dx%d" % img.size)


if __name__ == "__main__":
    main()
