#!/usr/bin/env python3
"""Render the Nov 24 2026 front page (1024x1024) from stories.json.
Original flat drawings; no external images; deterministic output."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
RED = (164, 31, 31)
DARKRED = (122, 20, 20)
NAVY = (27, 42, 74)
GREY = (90, 86, 78)
LIGHT = (232, 223, 198)

def find_font(names):
    for n in names:
        if os.path.exists(n):
            return n
    raise SystemExit("no font found: %s" % names)

SERIF_B = find_font(["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"])
SERIF = find_font(["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"])
SERIF_I = find_font(["/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"])
SANS_B = find_font(["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"])
SANS = find_font(["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])

_cache = {}
def F(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def para(d, x, y, text, font, maxw, fill=INK, lh=None):
    if lh is None:
        lh = int(font.size * 1.22)
    for ln in wrap(d, text, font, maxw):
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y

def text_h(d, text, font):
    return int(font.size * 1.22)

# ---------------- simplified world map (lon/lat polygons) ----------------
CONTINENTS = [
    [(-168,66),(-140,70),(-125,72),(-110,73),(-95,80),(-85,70),(-75,72),(-60,60),(-55,47),(-70,42),(-75,35),(-80,25),(-85,20),(-90,15),(-95,18),(-105,20),(-115,28),(-125,40),(-125,48),(-140,60),(-155,58),(-165,60)],
    [(-80,10),(-75,5),(-60,0),(-50,-5),(-35,-8),(-40,-20),(-48,-28),(-55,-35),(-65,-40),(-70,-50),(-73,-53),(-70,-40),(-70,-20),(-80,-5),(-80,5)],
    [(-10,36),(0,36),(10,38),(20,40),(28,36),(30,42),(28,45),(20,45),(12,44),(5,43),(-2,43),(-9,43),(-9,48),(-5,50),(0,51),(5,53),(8,57),(10,59),(18,56),(21,55),(24,58),(28,60),(30,62),(25,65),(20,70),(15,70),(10,68),(5,60),(0,58),(-5,55),(-10,50),(-10,43)],
    [(-17,15),(-15,25),(-10,30),(-5,35),(10,37),(20,32),(30,31),(35,28),(40,20),(43,12),(48,11),(51,10),(45,0),(40,-10),(35,-20),(32,-28),(25,-33),(18,-35),(15,-27),(12,-18),(10,-5),(8,4),(0,5),(-8,5),(-13,8),(-17,12)],
    [(30,42),(35,36),(40,38),(45,40),(50,38),(55,40),(60,25),(62,25),(58,22),(55,17),(50,25),(48,30),(55,30),(58,25),(60,20),(65,25),(70,20),(75,10),(78,8),(80,15),(85,20),(90,22),(92,18),(95,15),(100,8),(103,2),(105,10),(108,15),(110,20),(115,25),(120,30),(122,38),(127,40),(130,42),(135,45),(140,50),(142,55),(140,60),(135,65),(130,70),(120,72),(110,73),(100,75),(90,75),(80,72),(70,70),(60,68),(50,68),(40,65),(35,60),(30,55),(30,48),(30,45)],
    [(113,-22),(114,-30),(115,-35),(120,-34),(125,-32),(130,-32),(135,-35),(140,-38),(145,-38),(150,-37),(153,-32),(150,-25),(146,-19),(142,-15),(142,-11),(137,-12),(135,-15),(130,-12),(126,-14),(122,-17),(118,-20),(113,-22)],
]

REGION_COLOR = {r[0]: r[2] for r in DATA["edition"]["regions"]}
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---------------- flat illustrations ----------------
def sky(d, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)

def tower(d, x, y, w, h):
    sky(d, x, y, w, h, (22, 32, 63), (58, 74, 110))
    for sx, sy in [(x + 20, y + 12), (x + 90, y + 22), (x + 200, y + 10), (x + 280, y + 26), (x + 150, y + 8)]:
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 220))
    bx = x + w // 2 - 46
    d.rectangle([bx, y + 8, bx + 32, y + h], fill=(38, 52, 84))
    d.polygon([(bx - 4, y + 8), (bx + 36, y + 8), (bx + 16, y - 2)], fill=(52, 68, 104))
    for wy in range(y + 16, y + h - 6, 9):
        for wx in (bx + 5, bx + 14, bx + 23):
            d.rectangle([wx, wy, wx + 5, wy + 4], fill=(255, 209, 102))
    d.rectangle([x + w - 86, y + h - 52, x + w - 52, y + h], fill=(30, 42, 68))
    for wy in range(y + h - 46, y + h - 6, 9):
        for wx in (x + w - 80, x + w - 70, x + w - 60):
            d.rectangle([wx, wy, wx + 5, wy + 4], fill=(255, 209, 102))
    d.rectangle([x + 22, y + h - 34, x + 62, y + h], fill=(30, 42, 68))
    cx, cy = bx + 16, y + h // 2 - 6
    d.ellipse([cx - 17, cy - 10, cx + 17, cy + 10], fill=(255, 122, 26))
    d.ellipse([cx - 8, cy - 18, cx + 8, cy - 2], fill=(120, 120, 120))
    d.ellipse([cx + 2, cy - 20, cx + 15, cy - 8], fill=(150, 150, 150))
    d.ellipse([cx - 13, cy + 1, cx, cy + 14], fill=(90, 90, 90))
    d.polygon([(bx + 44, cy - 22), (bx + 56, cy - 17), (bx + 44, cy - 12)], fill=(220, 230, 235))

def shanghai(d, x, y, w, h):
    sky(d, x, y, w, h, (242, 166, 90), (122, 74, 107))
    d.ellipse([x + 18, y + 12, x + 50, y + 44], fill=(230, 90, 60))
    base = y + h
    blocks = [(x + 8, 22, 40), (x + 34, 18, 54), (x + 56, 24, 34), (x + 84, 16, 46),
              (x + 230, 22, 48), (x + 256, 18, 60), (x + 278, 24, 38), (x + 306, 16, 30)]
    for bx, bw, bh in blocks:
        d.rectangle([bx, base - bh, bx + bw, base], fill=(58, 47, 74))
        for wy in range(base - bh + 6, base - 6, 10):
            for wx in range(bx + 4, bx + bw - 5, 9):
                d.rectangle([wx, wy, wx + 4, wy + 3], fill=(255, 209, 102))
    px = x + w // 2 - 6
    d.rectangle([px, y + 24, px + 12, base], fill=(58, 47, 74))
    d.ellipse([px - 9, y + 30, px + 21, y + 54], fill=(190, 60, 60), outline=(255, 220, 200), width=1)
    d.ellipse([px - 6, y + 58, px + 18, y + 76], fill=(190, 60, 60), outline=(255, 220, 200), width=1)
    d.polygon([(px + 1, y + 24), (px + 11, y + 24), (px + 6, y + 6)], fill=(58, 47, 74))

def chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 33, 61))
    for gy in range(y + 14, y + h, 22):
        d.line([(x + 4, gy), (x + w - 4, gy)], fill=(48, 66, 102))
    pts = [(x + 8, y + h - 18), (x + 40, y + h - 40), (x + 80, y + h - 52), (x + 120, y + h - 78),
           (x + 160, y + h - 66), (x + 200, y + h - 30), (x + 240, y + h - 22), (x + 280, y + h - 48),
           (x + w - 8, y + h - 58)]
    d.line(pts, fill=(74, 222, 128), width=3)
    d.line(pts[4:], fill=(239, 68, 68), width=3)
    for i, (px, py) in enumerate(pts):
        if i in (0, 4, 8):
            d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255))

def court(d, x, y, w, h):
    sky(d, x, y, w, h, (214, 222, 232), (190, 196, 205))
    cx = x + w // 2
    d.polygon([(cx - 52, y + 4), (cx + 52, y + 4), (cx, y + 18)], fill=(120, 100, 70))
    d.rectangle([cx - 58, y + 18, cx + 58, y + 22], fill=(150, 130, 95))
    for i in range(5):
        ccx = cx - 50 + i * 21
        d.rectangle([ccx, y + 22, ccx + 10, y + h - 4], fill=(250, 244, 224))
        d.rectangle([ccx - 2, y + 22, ccx + 12, y + 25], fill=(232, 222, 198))
    d.rectangle([cx - 62, y + h - 6, cx + 62, y + h], fill=(150, 130, 95))
    d.rectangle([cx - 8, y + h - 16, cx + 8, y + h - 6], fill=(90, 70, 50))

def radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 48, 32))
    cx, cy = x + w // 2, y + h // 2 + 4
    for r in (34, 24, 14):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(74, 222, 128))
    d.line([(cx, cy - 34), (cx, cy + 34)], fill=(74, 222, 128))
    d.line([(cx - 34, cy), (cx + 34, cy)], fill=(74, 222, 128))
    d.polygon([(cx - 26, cy - 6), (cx + 10, cy - 2), (cx + 30, cy), (cx + 10, cy + 4), (cx - 26, cy + 8)], fill=(220, 230, 235))
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 80, 80))

def missile(d, x, y, w, h):
    sky(d, x, y, w, h, (43, 58, 85), (110, 124, 150))
    d.arc([x + 6, y - 34, x + w - 6, y + h + 14], 205, 335, fill=(255, 255, 255), width=3)
    mx, my = x + w // 2 + 6, y + 8
    d.polygon([(mx, my), (mx + 40, my + 8), (mx, my + 16)], fill=(230, 230, 230))
    d.polygon([(mx + 36, my + 4), (mx + 52, my + 8), (mx + 36, my + 12)], fill=(200, 60, 60))
    d.rectangle([mx + 8, my + 16, mx + 16, my + 22], fill=(200, 200, 200))
    d.polygon([(x + 30, y + h - 26), (x + 44, y + h - 4), (x + 58, y + h - 26)], fill=(255, 200, 60))
    d.text((x + 34, y + h - 22), "!", font=F(SANS_B, 16), fill=(120, 20, 20))

def smoke(d, x, y, w, h):
    sky(d, x, y, w, h, (226, 214, 186), (190, 170, 140))
    for bx, bw, bh in [(x + 6, 34, 26), (x + 46, 30, 36), (x + 82, 36, 22), (x + 124, 30, 30)]:
        d.rectangle([bx, y + h - bh, bx + bw, y + h], fill=(107, 90, 74))
        for wy in range(y + h - bh + 4, y + h - 4, 8):
            d.rectangle([bx + 5, wy, bx + 10, wy + 4], fill=(60, 50, 40))
    cx = x + w // 2 + 30
    d.ellipse([cx - 16, y + 2, cx + 8, y + 22], fill=(120, 118, 112))
    d.ellipse([cx - 6, y + 14, cx + 18, y + 34], fill=(150, 148, 142))
    d.ellipse([cx - 2, y + 28, cx + 16, y + 44], fill=(255, 122, 26))

def flats(d, x, y, w, h):
    sky(d, x, y, w, h, (60, 70, 92), (140, 130, 120))
    d.rectangle([x + 20, y + 8, x + w - 20, y + h], fill=(122, 106, 88))
    for r in range(3):
        for c in range(6):
            wx, wy = x + 30 + c * 24, y + 16 + r * 13
            col = (40, 34, 28) if (r * 6 + c) in (2, 9, 14) else (255, 209, 102)
            d.rectangle([wx, wy, wx + 12, wy + 8], fill=col)
    d.polygon([(x + w - 40, y + 2), (x + w - 10, y + 2), (x + w - 25, y + 18)], fill=(90, 86, 80))
    d.ellipse([x + w - 34, y + 16, x + w - 16, y + 32], fill=(255, 122, 26))

def chess(d, x, y, w, h):
    s = h // 4
    ox = x + 6
    for r in range(4):
        for c in range(4):
            col = (232, 220, 192) if (r + c) % 2 == 0 else (74, 59, 42)
            d.rectangle([ox + c * s, y + r * s, ox + (c + 1) * s, y + (r + 1) * s], fill=col)
    d.rectangle([ox, y, ox + 4 * s, y + 4 * s], outline=(40, 30, 20), width=2)
    kx, ky = ox + 4 * s + 16, y + 10
    d.rectangle([kx + 11, ky - 10, kx + 15, ky - 2], fill=(20, 20, 20))
    d.rectangle([kx + 8, ky - 7, kx + 18, ky - 3], fill=(20, 20, 20))
    d.ellipse([kx, ky, kx + 26, ky + 20], fill=(20, 20, 20))
    d.polygon([(kx + 1, ky + 18), (kx + 25, ky + 18), (kx + 21, ky + h - 4), (kx + 5, ky + h - 4)], fill=(20, 20, 20))
    nx = kx + 42
    d.polygon([(nx, y + h - 4), (nx + 13, y + 6), (nx + 26, y + h - 4)], fill=(245, 240, 225))
    d.rectangle([nx, y + h - 12, nx + 26, y + h - 4], fill=(245, 240, 225))

def football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 50))
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=(255, 255, 255), width=2)
    d.ellipse([x + w // 2 - 12, y + h // 2 - 12, x + w // 2 + 12, y + h // 2 + 12], outline=(255, 255, 255), width=2)
    d.rectangle([x + 8, y + 6, x + 34, y + h - 6], outline=(255, 255, 255), width=2)
    bx, by = x + w - 34, y + h // 2
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(255, 255, 255), outline=(20, 20, 20))
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(20, 20, 20))

def phone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 28, 40))
    px, py, pw, ph = x + w // 2 - 26, y + 3, 52, h - 6
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=4, fill=(220, 225, 235))
    d.rounded_rectangle([px + 4, py + 7, px + pw - 4, py + ph - 10], radius=2, fill=(40, 90, 160))
    d.text((px + 8, py + 12), "GROK", font=F(SANS_B, 11), fill=(255, 255, 255))
    d.polygon([(x + w - 22, y + h - 16), (x + w - 8, y + h - 16), (x + w - 15, y + h - 30)], fill=(255, 200, 60))
    d.text((x + w - 18, y + h - 16), "!", font=F(SANS_B, 12), fill=(120, 20, 20))

def quake(d, x, y, w, h):
    sky(d, x, y, w, h, (150, 170, 190), (200, 200, 190))
    d.polygon([(x, y + h), (x + w // 3, y + 8), (x + 2 * w // 3, y + h)], fill=(90, 107, 122))
    d.polygon([(x + w // 2, y + h), (x + 5 * w // 6, y + 14), (x + w, y + h)], fill=(70, 86, 100))
    d.polygon([(x + w // 3 - 14, y + 8), (x + w // 3 + 14, y + 8), (x + w // 3, y + 22)], fill=(245, 245, 240))
    pts = [(x + 10, y + h - 6), (x + 40, y + h - 14), (x + 70, y + h - 4), (x + 100, y + h - 16), (x + 130, y + h - 6), (x + w - 10, y + h - 12)]
    d.line(pts, fill=(164, 31, 31), width=3)

def blast(d, x, y, w, h):
    sky(d, x, y, w, h, (210, 200, 180), (170, 160, 145))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(80, 76, 70))
    d.rectangle([x + 14, y + h - 26, x + 62, y + h - 12], fill=(40, 40, 48))
    d.ellipse([x + 22, y + h - 14, x + 30, y + h - 6], fill=(15, 15, 15))
    d.ellipse([x + 46, y + h - 14, x + 54, y + h - 6], fill=(15, 15, 15))
    cx, cy = x + w - 40, y + 16
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 8, 20
        a = math.radians(ang)
        d.line([(cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], fill=(255, 140, 30), width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 60))

ART = {"tower": tower, "shanghai": shanghai, "chart": chart, "court": court,
       "radar": radar, "missile": missile, "smoke": smoke, "flats": flats,
       "chess": chess, "football": football, "phone": phone, "quake": quake,
       "blast": blast}

# ---------------- layout ----------------
def tag_chip(d, x, y, tag):
    colors = {"CONFIRMED": (46, 107, 52), "OFFICIAL": (164, 132, 20),
              "CLAIM": (164, 31, 31), "REPORTED": (31, 78, 121)}
    f = F(SANS_B, 10)
    tw = d.textlength(tag, font=f) + 10
    d.rounded_rectangle([x, y, x + tw, y + 14], radius=2, outline=colors[tag], width=1)
    d.text((x + 5, y + 1), tag, font=f, fill=colors[tag])
    return tw

def draw_masthead(d, ed):
    f_small = F(SANS_B, 14)
    d.text((10, 6), ed["masthead_left"], font=f_small, fill=RED)
    r = ed["masthead_right"]
    d.text((W - 10 - d.textlength(r, font=f_small), 6), r, font=f_small, fill=INK)
    d.line([(10, 28), (W - 10, 28)], fill=INK, width=2)
    f_date = F(SERIF_B, 58)
    t = ed["date_label"]
    d.text(((W - d.textlength(t, font=f_date)) / 2, 32), t, font=f_date, fill=INK)
    f_sub = F(SERIF_I, 19)
    s = ed["subhead"]
    d.text(((W - d.textlength(s, font=f_sub)) / 2, 96), s, font=f_sub, fill=DARKRED)
    d.line([(10, 122), (W - 10, 122)], fill=INK, width=1)

def draw_stats(d, ed):
    stats = ed["stats"]
    cw = (W - 20) // len(stats)
    f_n = F(SERIF_B, 28)
    f_l = F(SANS_B, 10)
    for i, (num, lab) in enumerate(stats):
        x0 = 10 + i * cw
        d.text((x0 + (cw - d.textlength(num, font=f_n)) / 2, 128), num, font=f_n, fill=INK)
        d.text((x0 + (cw - d.textlength(lab, font=f_l)) / 2, 160), lab, font=f_l, fill=GREY)
        if i:
            d.line([(x0, 130), (x0, 172)], fill=(200, 192, 172), width=1)
    d.line([(10, 178), (W - 10, 178)], fill=INK, width=1)

def draw_regions(d, ed):
    y = 182
    x = 10
    avail = W - 20
    wseg = avail // len(ed["regions"])
    f = F(SANS_B, 12)
    for name, n, col in ed["regions"]:
        d.rectangle([x, y, x + wseg - 1, y + 18], fill=hex2rgb(col))
        t = "%s %d" % (name, n)
        d.text((x + (wseg - d.textlength(t, font=f)) / 2, y + 2), t, font=f, fill=(255, 255, 255))
        x += wseg
    d.line([(10, 204), (W - 10, 204)], fill=INK, width=1)

def draw_timeline(d, ed):
    y = 208
    d.rectangle([10, y, 104, y + 18], fill=RED)
    d.text((15, y + 2), "THE DAY IN UTC", font=F(SANS_B, 11), fill=(255, 255, 255))
    f_t = F(SANS_B, 12)
    f_x = F(SANS, 12)
    x = 114
    for t, txt in ed["timeline"]:
        tw = d.textlength(t, font=f_t)
        d.text((x, y + 2), t, font=f_t, fill=RED)
        x += tw + 5
        xw = d.textlength(txt, font=f_x)
        d.text((x, y + 2), txt, font=f_x, fill=INK)
        x += xw + 14
        d.line([(x - 8, y + 3), (x - 8, y + 15)], fill=(200, 192, 172), width=1)
    d.line([(10, 230), (W - 10, 230)], fill=INK, width=1)

def draw_leads(d):
    y0, ah = 236, 88
    cols = [(10, 330), (347, 330), (684, 330)]
    for (x, w), lead in zip(cols, DATA["leads"]):
        ART[lead["art"]](d, x, y0, w, ah)
        d.rectangle([x, y0, x + 62, y0 + 18], fill=RED)
        d.text((x + 4, y0 + 2), lead["kicker"], font=F(SANS_B, 11), fill=(255, 255, 255))
        ly = y0 + ah + 6
        d.ellipse([x, ly + 2, x + 15, ly + 17], fill=hex2rgb(REGION_COLOR[lead["region"]]))
        d.text((x + 5, ly + 3), str(lead["n"]), font=F(SANS_B, 11), fill=(255, 255, 255))
        d.text((x + 20, ly + 2), lead["place"], font=F(SANS_B, 12), fill=hex2rgb(REGION_COLOR[lead["region"]]))
        tag_chip(d, x + w - 78, ly + 2, lead["tag"])
        hy = ly + 22
        hy = para(d, x, hy, lead["headline"], F(SERIF_B, 24), w, lh=26)
        para(d, x, hy + 2, lead["brief"], F(SANS, 13), w, lh=16)
    d.line([(10, 436), (W - 10, 436)], fill=INK, width=1)

def draw_mediums(d):
    rows = [(442, 40), (554, 40)]
    items = DATA["medium"]
    for ri, (y0, ah) in enumerate(rows):
        for ci in range(5):
            it = items[ri * 5 + ci]
            x = 10 + ci * 202
            w = 196
            ART[it["art"]](d, x, y0, w, ah)
            ly = y0 + ah + 4
            d.ellipse([x, ly + 1, x + 14, ly + 15], fill=hex2rgb(REGION_COLOR[it["region"]]))
            d.text((x + 4, ly + 2), str(it["n"]), font=F(SANS_B, 10), fill=(255, 255, 255))
            d.text((x + 18, ly + 2), it["place"], font=F(SANS_B, 11), fill=hex2rgb(REGION_COLOR[it["region"]]))
            tag_chip(d, x + w - 76, ly + 1, it["tag"])
            hy = ly + 20
            hy = para(d, x, hy, it["headline"], F(SANS_B, 14), w, lh=16)
            para(d, x, hy + 1, it["brief"], F(SANS, 11), w, lh=13)
    d.line([(10, 666), (W - 10, 666)], fill=INK, width=1)

def draw_map(d, ed):
    x0, y0, mw, mh = 10, 690, 260, 218
    d.text((x0, 672), "WHERE IT HAPPENED", font=F(SANS_B, 13), fill=RED)
    d.rectangle([x0, y0, x0 + mw, y0 + mh], fill=(215, 229, 234))
    def proj(lon, lat):
        px = x0 + (lon + 170) / 360.0 * mw
        py = y0 + (75 - lat) / 130.0 * mh
        return px, py
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(234, 223, 198), outline=(180, 168, 140))
    f_n = F(SANS_B, 10)
    for n, lat, lon in DATA["pins"]:
        px, py = proj(lon, lat)
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(164, 31, 31), outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((px - d.textlength(t, font=f_n) / 2, py - 7), t, font=f_n, fill=(255, 255, 255))
    ly = 906
    f_l = F(SANS, 11)
    for i, (name, n, col) in enumerate(ed["regions"]):
        lx = x0 + (i % 2) * 132
        yy = ly + (i // 2) * 13
        d.ellipse([lx, yy + 1, lx + 9, yy + 10], fill=hex2rgb(col))
        d.text((lx + 13, yy), name, font=f_l, fill=INK)

def draw_briefs(d, ed):
    x0 = 286
    d.text((x0, 672), "ALSO ON TUESDAY 24 NOVEMBER 2026", font=F(SANS_B, 13), fill=RED)
    d.line([(x0, 690), (W - 10, 690)], fill=(200, 192, 172), width=1)
    cols = [(x0, 358), (x0 + 370, 344)]
    f_n = F(SANS_B, 11)
    f_b = F(SANS_B, 11)
    f_t = F(SANS, 11)
    for ci, (cx, cw) in enumerate(cols):
        for ri in range(10):
            b = DATA["briefs"][ci * 10 + ri]
            n, place, text = b
            y = 696 + ri * 26
            d.ellipse([cx, y + 1, cx + 15, y + 16], fill=NAVY)
            t = str(n)
            d.text((cx + 7 - d.textlength(t, font=f_n) / 2, y + 2), t, font=f_n, fill=(255, 255, 255))
            tx = cx + 20
            head = place + ": "
            hw = d.textlength(head, font=f_b)
            avail = cw - 20
            lines = wrap(d, text, f_t, avail - hw)
            if len(lines) > 1:
                # keep one line: truncate the first line with an ellipsis
                first = lines[0]
                while d.textlength(first + "…", font=f_t) + hw > avail and len(first) > 8:
                    first = first[:-1]
                lines = [first + "…"]
            d.text((tx, y + 2), head, font=f_b, fill=INK)
            d.text((tx + hw, y + 2), lines[0], font=f_t, fill=INK)

def draw_datecheck(d, ed):
    y0 = 962
    d.rectangle([10, y0, W - 10, y0 + 32], outline=RED, width=2)
    f_l = F(SANS_B, 11)
    d.text((16, y0 + 3), "DATE CHECK", font=f_l, fill=RED)
    lw = d.textlength("DATE CHECK", font=f_l) + 12
    f_t = F(SANS, 11)
    lines = wrap(d, ed["date_check"], f_t, W - 20 - lw - 8)
    yy = y0 + 3
    for ln in lines[:2]:
        d.text((16 + lw, yy), ln, font=f_t, fill=INK)
        yy += 13

def draw_footer(d, ed):
    f = F(SANS, 10)
    d.text((10, 1002), ed["legend"], font=f, fill=GREY)
    s = ed["sources"]
    d.text((W - 10 - d.textlength(s, font=f), 1002), s, font=f, fill=GREY)

def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    ed = DATA["edition"]
    draw_masthead(d, ed)
    draw_stats(d, ed)
    draw_regions(d, ed)
    draw_timeline(d, ed)
    draw_leads(d)
    draw_mediums(d)
    draw_map(d, ed)
    draw_briefs(d, ed)
    draw_datecheck(d, ed)
    draw_footer(d, ed)
    out = os.path.join(HERE, "news.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
