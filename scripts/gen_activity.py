"""Generate assets/activity.svg from the GitHub contribution calendar (last 12 months).

Run: python3 scripts/gen_activity.py
Auth: GITHUB_TOKEN / GH_TOKEN, or `gh auth token` locally. Stdlib only.
"""
import datetime as dt
import json
import os
import pathlib
import subprocess
import urllib.request

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


cal = fetch()
days = sorted(cal)
n = len(days)
active = [1 if cal[d] else 0 for d in days]
roll = [sum(active[max(0, i - 29):i + 1]) for i in range(n)]  # active days in trailing 30

best = cur = 0
for a in active:
    cur = cur + 1 if a else 0
    best = max(best, cur)
now = 0
for a in reversed(active):  # ponytail: today with 0 commits yet counts as a break
    if not a:
        break
    now += 1

W, H, X0, X1, TOP, BASE = 1200, 240, 40, 1160, 80, 196
xf = lambda i: X0 + (X1 - X0) * i / (n - 1)
yf = lambda v: BASE - (BASE - TOP) * v / 30
pts = " ".join(f"{xf(i):.1f},{yf(roll[i]):.1f}" for i in range(n))

ticks = "".join(
    f'<line x1="{xf(i):.1f}" y1="{BASE}" x2="{xf(i):.1f}" y2="{BASE+4}" class="s"/>'
    f'<text x="{xf(i):.1f}" y="{BASE+16}" text-anchor="middle" class="t">{d.strftime("%b")}</text>'
    for i, d in enumerate(days) if d.day == 1)

stats = [(sum(active), "active days"), (best, "longest streak"), (now, "current streak"),
         (roll[-1], "of last 30 days")]
head = "".join(
    f'<text x="{X0 + k * 280}" y="40" class="v">{v}</text><text x="{X0 + k * 280}" y="58" class="t">{lbl}</text>'
    for k, (v, lbl) in enumerate(stats))

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Activity: {sum(active)} active days in the last year, longest streak {best}, {roll[-1]} of the last 30 days active"><title>GitHub activity, last 12 months</title>
<defs><radialGradient id="light" cx=".1" cy="0" r="1"><stop offset="0" stop-color="#2f6fd6" stop-opacity=".35"/><stop offset=".6" stop-color="#2f6fd6" stop-opacity="0"/></radialGradient>
<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f6fd6" stop-opacity=".45"/><stop offset="1" stop-color="#2f6fd6" stop-opacity="0"/></linearGradient></defs>
<rect width="{W}" height="{H}" rx="6" fill="#03070f"/><rect width="{W}" height="{H}" rx="6" fill="url(#light)"/>
<style>
:root{{--fg:#e8f0ff;--mut:#7f9cc9;--line:#9cc4ff}}
.v{{font:900 24px Georgia,'Times New Roman',serif;fill:var(--fg)}}
.t{{font:11px -apple-system,Segoe UI,Arial,sans-serif;fill:var(--mut)}}
.s{{stroke:var(--mut);stroke-opacity:.5}}
</style>
{head}
<line x1="{X0}" y1="{BASE}" x2="{X1}" y2="{BASE}" class="s"/>
<polygon points="{X0},{BASE} {pts} {X1},{BASE}" fill="url(#area)"/>
<polyline points="{pts}" fill="none" stroke="var(--line)" stroke-width="1.8" stroke-linejoin="round"/>
{ticks}
<text x="{X1}" y="{H-6}" text-anchor="end" class="t">rolling 30-day active days · updated {days[-1]}</text>
</svg>"""
OUT.write_text(svg, encoding="utf-8")
print(f"active={sum(active)} best={best} now={now} last30={roll[-1]} -> {OUT}")
