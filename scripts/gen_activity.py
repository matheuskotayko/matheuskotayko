"""Generate assets/activity.svg from the GitHub contribution calendar (last 12 months).

Run: python3 scripts/gen_activity.py
Auth: GITHUB_TOKEN / GH_TOKEN, or `gh auth token` locally. Stdlib only.
Shares palette and brush filters with gen_art.py.
"""
import collections
import datetime as dt
import json
import os
import pathlib
import random
import subprocess
import urllib.request

from gen_art import BLUE, GLOW, INK, MONO, PAPER, SERIF, VOID, splatter, svg

LOGIN = os.environ.get("GH_LOGIN", "matheuskotayko")
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "activity.svg"
QUERY = """query($login: String!) { user(login: $login) { contributionsCollection {
  contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") \
        or subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "activity-graph"})
    res = json.load(urllib.request.urlopen(req))
    if "errors" in res:
        raise SystemExit(res["errors"])
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {dt.date.fromisoformat(d["date"]): d["contributionCount"]
            for w in weeks for d in w["contributionDays"]}


def stats(cal):
    days = sorted(cal)
    active = [1 if cal[d] else 0 for d in days]
    roll = [sum(active[max(0, i - 29):i + 1]) for i in range(len(days))]  # active days in trailing 30
    best = cur = 0
    for a in active:
        cur = cur + 1 if a else 0
        best = max(best, cur)
    now = 0
    for a in reversed(active):  # ponytail: today with 0 commits yet counts as a break
        if not a:
            break
        now += 1
    return days, active, roll, best, now


def render(cal):
    days, active, roll, best, now = stats(cal)
    n, rng = len(days), random.Random(9)
    W, H, X0, X1, TOP, BASE = 1200, 430, 50, 1150, 190, 360
    xf = lambda i: X0 + (X1 - X0) * i / (n - 1)
    yf = lambda v: BASE - (BASE - TOP) * v / 30

    b = (f'<defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{GLOW}" stop-opacity=".45"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
         f'<filter id="glow"><feGaussianBlur stdDeviation="5"/></filter></defs>'
         f'<rect width="{W}" height="{H}" fill="url(#light)"/>')

    # Stat cards: big serif number lit from the left, label in mono, brush divider between.
    cards = [(sum(active), "active days", "last 12 months"), (best, "longest streak", "days in a row"),
             (now, "current streak", "days in a row"), (roll[-1], "last 30 days", "days active")]
    cw = (W - 2 * X0) / 4
    for k, (v, label, sub) in enumerate(cards):
        x = X0 + k * cw + 20
        b += (f'<text x="{x + 3}" y="{93}" font-family="{SERIF}" font-weight="900" font-size="58" fill="{VOID}" fill-opacity=".7">{v}</text>'
              f'<text x="{x}" y="{90}" font-family="{SERIF}" font-weight="900" font-size="58" fill="{PAPER}" filter="url(#rough)">{v}</text>'
              f'<text x="{x}" y="{122}" font-family="{MONO}" font-size="17" letter-spacing="3" fill="{GLOW}">{label.upper()}</text>'
              f'<text x="{x}" y="{144}" font-family="{MONO}" font-size="14" fill="{GLOW}" fill-opacity=".6">{sub}</text>')
        if k:
            b += f'<path d="M{x - 22},34 L{x - 18},150" stroke="{BLUE}" stroke-width="5" stroke-linecap="round" filter="url(#brush)" opacity=".8"/>'

    # Monthly skyline: one ink column per month, height = active days that month.
    months = collections.OrderedDict()
    for i, d in enumerate(days):
        months.setdefault((d.year, d.month), []).append(i)
    for idx in months.values():
        x0, x1 = xf(idx[0]) + 3, xf(idx[-1]) - 3
        h = (BASE - TOP) * sum(active[i] for i in idx) / 31
        b += f'<rect x="{x0:.1f}" y="{BASE - h:.1f}" width="{x1 - x0:.1f}" height="{h:.1f}" fill="{INK}" fill-opacity=".55" filter="url(#rough)"/>'

    # Grid at 10/20/30 active days.
    for v in (10, 20, 30):
        b += (f'<line x1="{X0}" y1="{yf(v):.1f}" x2="{X1}" y2="{yf(v):.1f}" stroke="{GLOW}" stroke-opacity=".12" stroke-dasharray="2 6"/>'
              f'<text x="{X1 + 8}" y="{yf(v) + 5:.1f}" font-family="{MONO}" font-size="13" fill="{GLOW}" fill-opacity=".55">{v}</text>')

    pts = " ".join(f"{xf(i):.1f},{yf(roll[i]):.1f}" for i in range(n))
    b += (f'<polygon points="{X0},{BASE} {pts} {X1},{BASE}" fill="url(#area)"/>'
          f'<polyline points="{pts}" fill="none" stroke="{GLOW}" stroke-width="6" stroke-opacity=".5" filter="url(#glow)"/>'
          f'<polyline points="{pts}" fill="none" stroke="{PAPER}" stroke-width="2.6" stroke-linejoin="round"/>'
          f'<path d="M{X0 - 10},{BASE} L{X1 + 10},{BASE}" stroke="{BLUE}" stroke-width="4" filter="url(#brush)"/>')

    for i, d in enumerate(days):
        if d.day == 1:
            b += f'<text x="{xf(i):.1f}" y="{BASE + 28}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{GLOW}">{d.strftime("%b")}</text>'

    # Peak: small ensō + value. Now: pulsing point.
    pk = max(range(n), key=lambda i: (roll[i], i))
    px, py = xf(pk), yf(roll[pk])
    b += (f'<path d="M{px + 14},{py - 6} A15,15 0 1 1 {px + 9},{py - 12}" fill="none" stroke="{GLOW}" stroke-width="3" stroke-linecap="round" filter="url(#rough)"/>'
          f'<text x="{px}" y="{py - 26}" text-anchor="middle" font-family="{MONO}" font-size="14" letter-spacing="2" fill="{PAPER}">PEAK {roll[pk]}</text>')
    nx, ny = xf(n - 1), yf(roll[-1])
    b += (f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="6" fill="{PAPER}"/>'
          f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="6" fill="none" stroke="{PAPER}" stroke-width="2">'
          f'<animate attributeName="r" values="6;18" dur="2s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/></circle>')

    b += splatter(rng, 14, 900, 1180, 160, 200, GLOW, 1.6)
    b += (f'<text x="{X0}" y="{H - 14}" font-family="{MONO}" font-size="14" fill="{GLOW}" fill-opacity=".75">'
          f'line: active days in the trailing 30 · columns: active days per month</text>'
          f'<text x="{X1}" y="{H - 14}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{GLOW}" fill-opacity=".75">updated {days[-1]}</text>')
    title = (f"Activity: {sum(active)} active days in the last year, longest streak {best}, "
             f"current streak {now}, {roll[-1]} of the last 30 days active, peak {roll[pk]}")
    return svg(W, H, b, title), (sum(active), best, now, roll[-1])


if __name__ == "__main__":
    out, s = render(fetch())
    OUT.write_text(out, encoding="utf-8")
    print(f"active={s[0]} best={s[1]} now={s[2]} last30={s[3]} -> {OUT}")
