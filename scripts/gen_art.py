"""Generate the static README artwork: blue chiaroscuro, sumi-e brush ink.

Run: python3 scripts/gen_art.py  ->  writes assets/banner.svg and assets/sec*.svg
Static art, run by hand when you change it. Stdlib only.
"""
import pathlib
import random

OUT = pathlib.Path(__file__).resolve().parent.parent / "assets"

VOID, INK, BLUE, GLOW, PAPER = "#03070f", "#0a1426", "#2f6fd6", "#9cc4ff", "#e8f0ff"
SERIF = "'Noto Serif CJK JP','Yu Mincho','Hiragino Mincho ProN',Georgia,'Times New Roman',serif"
MONO = "SFMono-Regular,Consolas,'Liberation Mono',monospace"

# Filters do the "brush" work: turbulence displaces clean shapes into dry-brush edges.
DEFS = f"""<defs>
<filter id="brush" x="-10%" y="-30%" width="120%" height="160%">
  <feTurbulence type="fractalNoise" baseFrequency=".035 .9" numOctaves="3" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="14" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="3" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="3"/>
</filter>
<filter id="wash" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency=".012 .05" numOctaves="4" seed="11" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="40"/>
  <feGaussianBlur stdDeviation="1.2"/>
</filter>
<filter id="grain">
  <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5"/>
  <feColorMatrix values="0 0 0 0 .6  0 0 0 0 .75  0 0 0 0 1  0 0 0 .07 0"/>
</filter>
<radialGradient id="light" cx=".18" cy=".05" r=".9">
  <stop offset="0" stop-color="{GLOW}" stop-opacity=".55"/>
  <stop offset=".25" stop-color="{BLUE}" stop-opacity=".28"/>
  <stop offset=".6" stop-color="{BLUE}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="slash" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{PAPER}" stop-opacity="0"/>
  <stop offset=".35" stop-color="{PAPER}" stop-opacity=".95"/>
  <stop offset="1" stop-color="{GLOW}" stop-opacity=".15"/>
</linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{BLUE}"/>
  <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
</linearGradient>
</defs>"""


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{DEFS}'
            f'<rect width="{w}" height="{h}" fill="{VOID}"/>{body}'
            f'<rect width="{w}" height="{h}" filter="url(#grain)"/></svg>')


def ridge(rng, w, base, amp, step):
    """Jagged mountain silhouette, closed down to the bottom edge."""
    pts, x = [], -40
    while x < w + 60:
        pts.append(f"{x},{base - rng.uniform(0, amp):.0f}")
        x += rng.uniform(step * .6, step * 1.4)
    return f"M-40,{base + 400} L{' L'.join(pts)} L{w + 60},{base + 400} Z"


def splatter(rng, n, x0, x1, y0, y1, color, rmax):
    return "".join(
        f'<circle cx="{rng.uniform(x0, x1):.0f}" cy="{rng.uniform(y0, y1):.0f}" '
        f'r="{rng.uniform(.6, rmax):.1f}" fill="{color}" fill-opacity="{rng.uniform(.3, .9):.2f}"/>'
        for _ in range(n))


def banner():
    W, H, rng = 1200, 420, random.Random(42)
    b = f'<rect width="{W}" height="{H}" fill="url(#light)"/>'
    # Three ink-wash ridges, the farthest catches the most light.
    for base, amp, fill, op in [(250, 120, BLUE, .22), (310, 90, INK, .95), (370, 60, VOID, 1)]:
        b += f'<path d="{ridge(rng, W, base, amp, 70)}" fill="{fill}" fill-opacity="{op}" filter="url(#wash)"/>'
    # Rim light along the middle ridge: chiaroscuro edge.
    b += f'<path d="{ridge(random.Random(42 + 1), W, 310, 90, 70)}" fill="none" stroke="{GLOW}" stroke-opacity=".25" stroke-width="1.5" filter="url(#wash)"/>'
    # Enso: one open brush circle, half swallowed by the dark.
    b += (f'<path d="M1080,95 A125,125 0 1 1 905,140" fill="none" stroke="{BLUE}" stroke-opacity=".45" '
          f'stroke-width="26" stroke-linecap="round" filter="url(#brush)"/>'
          f'<path d="M1074,100 A118,118 0 1 1 912,146" fill="none" stroke="{GLOW}" stroke-opacity=".3" '
          f'stroke-width="3" filter="url(#rough)"/>')
    # The sword cut: one tapered brush slash across the frame.
    b += (f'<path d="M420,372 C640,300 900,150 1170,30 C900,175 660,320 430,386 Z" fill="url(#slash)" filter="url(#brush)"/>'
          f'<path d="M480,370 C700,290 930,160 1140,52" fill="none" stroke="{GLOW}" stroke-opacity=".35" stroke-width="1" filter="url(#rough)"/>')
    b += splatter(rng, 40, 700, 1180, 20, 160, PAPER, 2.6)
    b += splatter(rng, 25, 40, 400, 290, 400, GLOW, 1.8)
    # Name: lit from the upper left, shadow falling right.
    b += (f'<text x="74" y="168" font-family="{SERIF}" font-weight="900" font-size="78" letter-spacing="6" '
          f'fill="{VOID}" fill-opacity=".85" filter="url(#rough)">MATHEUS</text>'
          f'<text x="68" y="162" font-family="{SERIF}" font-weight="900" font-size="78" letter-spacing="6" '
          f'fill="{PAPER}" filter="url(#rough)">MATHEUS</text>'
          f'<text x="70" y="214" font-family="{SERIF}" font-weight="400" font-size="34" letter-spacing="18" '
          f'fill="{GLOW}" fill-opacity=".85" filter="url(#rough)">FLECK</text>')
    b += (f'<rect x="70" y="236" width="300" height="2" fill="url(#fade)"/>'
          f'<text x="70" y="262" font-family="{MONO}" font-size="14" letter-spacing="2" fill="{GLOW}" fill-opacity=".75">'
          f'BACKEND · AI SYSTEMS · SECURITY</text>')
    b += f'<rect x="0" y="{H - 3}" width="{W}" height="3" fill="url(#fade)"/>'
    return svg(W, H, b, "Matheus Fleck — backend, AI systems and security. Ink-wash mountains lit in blue, a brush slash and an ensō circle.")


def section(n, numeral, title):
    W, H, rng = 1200, 96, random.Random(n)
    b = (f'<rect width="{W}" height="{H}" fill="url(#light)"/>'
         f'<text x="40" y="74" font-family="{SERIF}" font-weight="900" font-size="54" fill="{BLUE}" '
         f'fill-opacity=".9" filter="url(#brush)">{numeral}</text>'
         f'<text x="150" y="44" font-family="{MONO}" font-size="12" letter-spacing="4" fill="{GLOW}" fill-opacity=".6">'
         f'CHAPTER {n:02d}</text>'
         f'<text x="148" y="78" font-family="{SERIF}" font-weight="900" font-size="32" letter-spacing="5" '
         f'fill="{PAPER}" filter="url(#rough)">{title.upper()}</text>'
         f'<path d="M150,88 C400,82 800,86 1180,80 L1180,82 C800,90 400,90 120,92 Z" fill="url(#fade)" filter="url(#brush)"/>')
    b += splatter(rng, 12, 900, 1180, 10, 70, GLOW, 1.6)
    return svg(W, H, b, f"Chapter {n}: {title}")


SECTIONS = [("I", "Origin"), ("II", "Activity"), ("III", "Projects"), ("IV", "Arsenal")]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    for n, (k, t) in enumerate(SECTIONS, 1):
        (OUT / f"sec{n}.svg").write_text(section(n, k, t), encoding="utf-8")
    print(f"wrote banner + {len(SECTIONS)} sections -> {OUT}")
