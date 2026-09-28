"""만트라 3주 하이라이트 영상 (인스타 릴스 1080x1920, 10초, 무음)을 만든다.

필요: python3 + Pillow, ffmpeg, 한글 폰트(Noto Sans CJK 또는 나눔고딕)
실행: python3 highlight/make_video.py
"""
import glob
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mantra-3weeks.mp4")

BG = (0, 0, 0)
TEXT = (246, 241, 234)
SUB = (170, 163, 155)
GOLD = (255, 201, 120)
PINK = (255, 122, 168)

# (시작초, 끝초, 종류, 번호, 제목, 설명)
SCENES = [
    (0.0, 1.2, "intro", "", "3주,\n앱 하나", "Claude와 함께 만든 기록"),
    (1.2, 2.5, "card", "01", "기도 앱\n첫 버전", "염주 · 목탁 · 싱잉볼 · 사찰 기도"),
    (2.5, 3.8, "card", "02", "진짜 같은\n디자인", "3D 목탁 · 싱잉볼 · 움직이는 채"),
    (3.8, 5.1, "card", "03", "진짜\n목탁 소리", "직접 녹음한 소리 그대로"),
    (5.1, 6.4, "stat", "04", "2.9초\n→ 0.9초", "첫 화면 로딩 3배 빠르게"),
    (6.4, 7.7, "card", "05", "이름은\n'만트라' ♥", "핑크 하트 아이콘 · 인기 사찰 3곳"),
    (7.7, 9.0, "card", "06", "구글 플레이\n준비 완료", "앱 등록 준비물 · 공식 주소"),
    (9.0, 10.0, "outro", "", "만트라", "Made with Claude"),
]
DURATION = 10.0


def find_font(bold):
    pats = (
        ["NotoSansCJK*-Black*", "NotoSansCJK*-Bold*", "NotoSansKR*Bold*", "NanumGothic*ExtraBold*", "NanumGothic*Bold*"]
        if bold
        else ["NotoSansCJK*-Medium*", "NotoSansCJK*-Regular*", "NotoSansKR*", "NanumGothic.ttf", "NanumGothic*"]
    )
    roots = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
             os.path.expanduser("~/.local/share/fonts"), os.path.dirname(os.path.abspath(__file__))]
    for p in pats:
        for r in roots:
            hit = sorted(glob.glob(os.path.join(r, "**", p), recursive=True))
            if hit:
                return hit[0]
    raise SystemExit("한글 폰트를 찾지 못했습니다. fonts-noto-cjk 또는 나눔고딕을 설치하세요.")


BOLD, REG = find_font(True), find_font(False)
_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        # .ttc 는 index 1 이 KR 인 경우가 많다
        idx = 1 if path.endswith(".ttc") else 0
        try:
            _cache[key] = ImageFont.truetype(path, size, index=idx)
        except OSError:
            _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def draw_center(d, y, text, f, fill, spacing=10):
    box = d.multiline_textbbox((0, 0), text, font=f, spacing=spacing, align="center")
    w = box[2] - box[0]
    d.multiline_text(((W - w) / 2 - box[0], y), text, font=f, fill=fill, spacing=spacing, align="center")
    return box[3] - box[1]


def blend(c, a):
    return tuple(int(v * a) for v in c)  # 검정 배경 위 투명도 흉내


def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for i, (s, e, kind, num, title, sub) in enumerate(SCENES):
        if not (s <= t < e):
            continue
        local = t - s
        a_in = ease_out(local / 0.22)
        a_out = 1.0 if kind == "outro" else min(1.0, (e - t) / 0.12)
        a = a_in * a_out
        rise = (1 - a_in) * 90

        # 뒤쪽 은은한 빛 (염주 뒤 빛 느낌)
        glow = GOLD if kind != "card" or num != "05" else PINK
        for r in range(520, 0, -40):
            k = (1 - r / 520) * 0.10 * a
            d.ellipse((W / 2 - r, 820 - r, W / 2 + r, 820 + r), fill=blend(glow, k))

        if kind in ("card", "stat"):
            draw_center(d, 470 + rise, num, font(BOLD, 150), blend(GOLD, a))
            tf = font(BOLD, 150 if kind == "stat" else 128)
            draw_center(d, 700 + rise, title, tf, blend(PINK if kind == "stat" else TEXT, a), spacing=24)
            draw_center(d, 1120 + rise * 0.6, sub, font(REG, 52), blend(SUB, a))
            # 진행 점 (01~06)
            n = int(num)
            for j in range(6):
                cx = W / 2 + (j - 2.5) * 44
                on = j < n
                rr = 10 if j == n - 1 else 7
                d.ellipse((cx - rr, 1330 - rr, cx + rr, 1330 + rr), fill=blend(GOLD if on else (70, 66, 62), a))
        elif kind == "intro":
            scale = 1 + (1 - a_in) * 0.15
            draw_center(d, 640 + rise, title, font(BOLD, int(170 * scale)), blend(TEXT, a), spacing=30)
            draw_center(d, 1120, sub, font(REG, 54), blend(GOLD, a))
        else:  # outro
            draw_center(d, 690 + rise, "♥", font(BOLD, 150), blend(PINK, a))
            draw_center(d, 880 + rise, title, font(BOLD, 190), blend(TEXT, a))
            draw_center(d, 1130, sub, font(REG, 54), blend(GOLD, a))
    return img


def main():
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
           "-movflags", "+faststart", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DURATION * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg 실패")
    print("완성:", OUT)


if __name__ == "__main__":
    main()
