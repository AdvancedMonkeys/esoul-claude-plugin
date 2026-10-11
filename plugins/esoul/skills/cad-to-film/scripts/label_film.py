#!/usr/bin/env python3
"""
Labels over a Render Studio film, pinned to the points the render recorded frame by frame.

    python3 label_film.py FILM.mp4 CAMERA.json PLAN.json OUT.mp4 [--font /path/Sans.ttf] [--check]

FILM.mp4      the film from Render Studio (Renders/<title>.mp4)
CAMERA.json   its "<title> — camera.json" (written when the scene had `anchors`)
PLAN.json     what to draw, in film seconds:
  {
    "kicker":   "THE MAIN MAGNET",                                   # small heading, top left, whole shot
    "title":    { "text": "HOW AN MRI WORKS", "sub": "magnets and radio", "on": 1.0, "off": 6.5 },
    "labels":   [ { "anchor": "coil", "text": "Main coils", "sub": "Nb-Ti at 4 K",
                    "color": "#58C4DD", "on": 2.0, "off": 9.0, "offset": [150, -110] } ],
    "captions": [ { "text": "one turn every 3.86 s", "on": 4, "off": 9 } ],   # bottom centre, on a dark band
    "length":   24.5                                                 # optional: cut or hold the last frame to this
  }
  `anchor` is an id from the scene's `anchors`; `offset` is where the box sits from that point, in pixels (a
  negative x puts the box to the left). Every element fades in and out over 0.4 s.

--check   only report problems (labels overlapping each other or the kicker, anchors that are off screen while
          their label is on, anchors the camera never saw) and write nothing.

Needs Pillow and ffmpeg. Nothing else.
"""
import argparse, json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"]
BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]
BG, TXT, GREY = (11, 14, 20), (245, 241, 230), (150, 158, 176)
FADE = 0.4

def font(paths, size, override=None):
    for p in ([override] if override else []) + paths:
        if p and os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def smooth(a, b, t):
    x = min(1.0, max(0.0, (t - a) / max(b - a, 1e-6))); return x * x * (3 - 2 * x)

def alpha(item, t):
    return smooth(item["on"], item["on"] + FADE, t) * (1 - smooth(item["off"] - FADE, item["off"], t))

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-show_entries", "format=duration", "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j["streams"][0]; n, d = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(n) / float(d), float(j["format"]["duration"])

class Painter:
    def __init__(self, W, H, fontpath):
        k = H / 720
        self.W, self.H, self.k = W, H, k
        self.lab, self.sub = font(FONTS, int(22 * k), fontpath), font(FONTS, int(17 * k), fontpath)
        self.kick, self.cap = font(BOLD, int(19 * k), fontpath), font(FONTS, int(24 * k), fontpath)
        self.big, self.bigsub = font(BOLD, int(54 * k), fontpath), font(FONTS, int(24 * k), fontpath)
        self.top = int(56 * k)  # labels never enter the kicker band

    def box(self, dr, xy, lb):
        k = self.k; x, y = xy; ox, oy = lb.get("offset", [140, -90])
        tw = max(dr.textlength(lb["text"], font=self.lab), dr.textlength(lb.get("sub", ""), font=self.sub) if lb.get("sub") else 0)
        pad = 11 * k; bh = 36 * k + (26 * k if lb.get("sub") else 0); bw = tw + 2 * pad
        bx = x + ox if ox >= 0 else x + ox - bw
        by = y + oy - bh / 2
        bx = min(max(bx, 12 * k), self.W - bw - 12 * k); by = min(max(by, self.top), self.H - bh - 12 * k)
        return bx, by, bw, bh

    def label(self, dr, a, xy, lb):
        k = self.k; x, y = xy; col = rgb(lb.get("color", "#58C4DD"))
        bx, by, bw, bh = self.box(dr, xy, lb)
        A = lambda c, m=1.0: tuple(c) + (int(255 * a * m),)
        ex = bx if lb.get("offset", [140])[0] >= 0 else bx + bw
        dr.line([(x, y), (ex, by + bh / 2)], fill=A(col, 0.9), width=max(2, int(2.5 * k)))
        r = 6 * k
        dr.ellipse([x - r, y - r, x + r, y + r], fill=A(col), outline=A(BG), width=max(1, int(2 * k)))
        dr.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(8 * k), fill=A(BG, 0.82), outline=A(col, 0.9), width=max(1, int(2 * k)))
        dr.text((bx + 11 * k, by + 6 * k), lb["text"], font=self.lab, fill=A(TXT))
        if lb.get("sub"): dr.text((bx + 11 * k, by + 36 * k), lb["sub"], font=self.sub, fill=A(GREY))

    def band(self, dr, y0, y1, a, peak=210):
        # a soft dark band: type stays readable over white and brass alike
        mid = (y0 + y1) / 2; half = max(1, (y1 - y0) / 2)
        for yy in range(int(y0), int(y1)):
            d = abs(yy - mid) / half
            dr.line([(0, yy), (self.W, yy)], fill=(5, 7, 12, int(peak * a * max(0.0, 1 - d * d))))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("film"); ap.add_argument("camera"); ap.add_argument("plan"); ap.add_argument("out", nargs="?")
    ap.add_argument("--font"); ap.add_argument("--check", action="store_true")
    o = ap.parse_args()
    if not shutil.which("ffmpeg"): sys.exit("ffmpeg is needed (and ffprobe)")
    W, H, FPS, dur = probe(o.film)
    cam = json.load(open(o.camera)); plan = json.load(open(o.plan))
    start = cam.get("frameStart", 1)
    by_frame = {c["frame"] - start: c.get("anchors", {}) for c in cam["frames"]}
    labels = plan.get("labels", []); length = float(plan.get("length", dur)); n = int(round(length * FPS))
    P = Painter(W, H, o.font)
    probe_img = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    # ---- the check: what a viewer would see go wrong
    problems, seen = [], set(a for f in by_frame.values() for a in f)
    for lb in labels:
        if lb["anchor"] not in seen: problems.append(f'label "{lb["text"]}": anchor "{lb["anchor"]}" is not in camera.json (add it to the scene\'s anchors)')
    spans = {}
    def note(key, t):
        s = spans.setdefault(key, [t, t]); s[1] = t
    for i in range(n):
        t = i / FPS; anc = by_frame.get(min(i, max(by_frame) if by_frame else 0), {})
        boxes = []
        for lb in labels:
            if alpha(lb, t) < 0.5: continue
            p = anc.get(lb["anchor"])
            if not p: continue
            if not p[2]: note(f'"{lb["text"]}" points at something off screen', t); continue
            bx, by, bw, bh = P.box(probe_img, (p[0], p[1]), lb); boxes.append((lb["text"], bx, by, bw, bh))
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                A_, B_ = boxes[a], boxes[b]
                if A_[1] < B_[1] + B_[3] and B_[1] < A_[1] + A_[3] and A_[2] < B_[2] + B_[4] and B_[2] < A_[2] + A_[4]:
                    note(f'"{A_[0]}" and "{B_[0]}" overlap', t)
    for k, (t0, t1) in spans.items(): problems.append(f"{k} from {t0:.1f} s to {t1:.1f} s")
    for p in problems: print("CHECK:", p)
    if o.check:
        print("CHECK: clean" if not problems else f"CHECK: {len(problems)} problem(s)"); return
    if not o.out: sys.exit("give an output path (or --check)")

    src = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", o.film, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", f"{FPS}", "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-an", o.out], stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        b = src.stdout.read(W * H * 3)
        im = Image.frombytes("RGB", (W, H), b) if len(b) == W * H * 3 else (last.copy() if last else Image.new("RGB", (W, H)))
        last = im
        t = i / FPS; anc = by_frame.get(min(i, max(by_frame) if by_frame else 0), {})
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        for lb in labels:
            a = alpha(lb, t); p = anc.get(lb["anchor"])
            if a > 0.01 and p and p[2]: P.label(dr, a, (p[0], p[1]), lb)
        for c in plan.get("captions", []):
            a = alpha(c, t)
            if a > 0.01:
                P.band(dr, H - 150 * P.k, H, a)
                dr.text((W / 2, H - 46 * P.k), c["text"], font=P.cap, fill=(244, 211, 69, int(255 * a)), anchor="ms")
        if plan.get("kicker"): dr.text((34 * P.k, 30 * P.k), plan["kicker"], font=P.kick, fill=(150, 158, 176, 255))
        ti = plan.get("title")
        if ti:
            a = alpha(ti, t)
            if a > 0.01:
                P.band(dr, H / 2 - 110 * P.k, H / 2 + 80 * P.k, a)
                dr.text((W / 2 + 2, H / 2 - 28 * P.k + 2), ti["text"], font=P.big, fill=(0, 0, 0, int(160 * a)), anchor="mm")
                dr.text((W / 2, H / 2 - 28 * P.k), ti["text"], font=P.big, fill=TXT + (int(255 * a),), anchor="mm")
                if ti.get("sub"): dr.text((W / 2, H / 2 + 26 * P.k), ti["sub"], font=P.bigsub, fill=(126, 214, 236, int(245 * a)), anchor="mm")
        enc.stdin.write(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB").tobytes())
    enc.stdin.close(); enc.wait(); src.kill()
    print(f"wrote {o.out}: {n} frames, {n / FPS:.2f} s")

if __name__ == "__main__":
    main()
