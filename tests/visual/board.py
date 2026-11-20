"""
Visual progress board: the UI reference next to the live app, screen by screen.

For every screen it captures the reference, captures the live app with the SAME
data, measures how many pixels differ, and writes one HTML page with reference,
live, difference image and a match score.

    python -m tests.visual.board ref      capture the reference (no server needed)
    python -m tests.visual.board live     capture the live app (start it first: ./run.sh real)
    python -m tests.visual.board build    compare and write the board
    python -m tests.visual.board all      all three

How "same data" works
  The reference's Simple dashboard carries its own mock API (mockApi). While the
  live Simple page is captured, every /api call it makes is answered by that
  mock, running in a hidden copy of the reference. So any difference on the
  board is a real difference in the frontend, not in the data.

Where things go (outside the repo, in the workspace):
  <workspace>/progress/index.html, ref/, live/, diff/, scores.json
Override with TUTOR_WORKSPACE, UI_REFERENCE, TUTOR_PROGRESS_DIR, TUTOR_BASE_URL.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlsplit

REPO = Path(__file__).resolve().parents[2]
WORKSPACE = Path(os.environ.get("TUTOR_WORKSPACE", REPO.parent))
REFERENCE = Path(os.environ.get("UI_REFERENCE", WORKSPACE / "reference" / "Hackathon-IIT-Mandi-Layout.html"))
OUT = Path(os.environ.get("TUTOR_PROGRESS_DIR", WORKSPACE / "progress"))
CACHE = OUT / ".cache"
BASE_URL = os.environ.get("TUTOR_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
VIEWPORT = {"width": 1440, "height": 900}
FIXED_NOW = "2026-11-16T10:00:00"        # both sides see the same "today"
MATCH, CLOSE = 0.005, 0.05                # share of differing pixels: match <= 0.5%, close <= 5%
TOLERANCE = 24                            # per-channel difference (0-255) that counts as "different"

# --------------------------------------------------------------------------- #
# Screens
# --------------------------------------------------------------------------- #

JS_HELPERS = """
const S = ms => new Promise(r => setTimeout(r, ms));
const L = async (email) => { document.getElementById('loginEmail').value = email; doLogin(); await S(700); };
const C = async (msg) => { document.getElementById('chatInput').value = msg; sendChatMessage(); await S(700); };
const pick = async (i) => {
  if (typeof pickQuizOption !== 'function') throw new Error('this page has no multiple-choice quiz yet');
  pickQuizOption(i); await S(100);
};
const next = async () => { nextQuizStep(); await S(500); };
"""
_STUDENT = "await L('student@gmail.com');"
_TO_S1 = _STUDENT + " chooseDashboard('simple'); await S(800);"
_PRE = " startQuiz('pre'); await S(700); await pick(1); await next(); await pick(1); await next(); await pick(0); await next();"
_CHAT = " setScreen('s2'); await S(200); await C('How do I add fractions with different denominators?'); await C('2/6'); await C('3/6');"
_POST = " await C('3/4'); startQuiz('post'); await S(700); await pick(1); await next(); await pick(1); await next(); await pick(0); await next(); await S(300);"
_TEACHER = "await L('teacher@school.edu'); document.getElementById('lookupEmail').value = 'demo'; lookupStudent(); await S(700);"

# (key, title, steps run inside the page)
SIMPLE = [
    ("simple-01-login", "Login", ""),
    ("simple-02-chooser", "Dashboard chooser", _STUDENT),
    ("simple-03-s1-start", "S1 · Start a session", _TO_S1),
    ("simple-04-s1-placement-quiz", "S1 · Placement quiz", _TO_S1 + " startQuiz('pre'); await S(700); await pick(0);"),
    ("simple-05-s2-tutoring", "S2 · Tutoring session", _TO_S1 + _PRE + _CHAT),
    ("simple-06-s3-session-end", "S3 · Session end", _TO_S1 + _PRE + _CHAT + _POST),
    ("simple-07-t1-lookup", "T1 · Student lookup", _TEACHER),
    ("simple-08-t2-metrics", "T2 · Eval metrics", _TEACHER + " setScreen('t2'); await S(700);"),
    ("simple-09-t3-graph", "T3 · Misconception graph", _TEACHER + " setScreen('t3'); document.getElementById('graphConcept').value = 'Fractions'; loadMisconceptionGraph(); await S(700);"),
    ("simple-10-t4-escalations", "T4 · Escalation feed", _TEACHER + " setScreen('t4'); await S(700);"),
    ("simple-11-t5-memory", "T5 · Memory impact", _TEACHER + " setScreen('t5'); await S(100);"),
]

GAMIFIED_SCREENS = [
    "landing", "signin", "mainmenu", "welcome", "avatarselect", "howitworks", "pretest", "lesson", "posttest",
    "progress", "sessioncomplete", "reward", "freequest", "leaderboard", "evalmetrics", "misconceptions",
    "spacedrepeat", "switchstudent",
]
GAMIFIED = [(f"gamified-{i:02d}-{name}", name) for i, name in enumerate(GAMIFIED_SCREENS, 1)]
NO_PLAYER = {"landing", "signin"}        # shown before a player exists

# --------------------------------------------------------------------------- #
# Browser helpers
# --------------------------------------------------------------------------- #

SEED_RANDOM = "(() => { let s = 20261116; Math.random = () => (s = (s * 16807) % 2147483647) / 2147483647; })();"
SETTLE = """() => {
  for (const a of document.getAnimations()) {
    try {
      const t = a.effect && a.effect.getComputedTiming();
      if (t && t.iterations === Infinity) { a.currentTime = 0; a.pause(); } else { a.finish(); }
    } catch (e) {}
  }
  if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  window.scrollTo(0, 0);
}"""


def _browser(p):
    return p.chromium.launch(channel="chrome", headless=True, args=["--hide-scrollbars"])


def _context(browser):
    ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1, color_scheme="light", locale="en-GB")
    ctx.add_init_script(SEED_RANDOM)
    return ctx


def _settle_and_shoot(page, path: Path) -> None:
    page.evaluate("() => document.fonts.ready.then(() => true)")
    page.add_style_tag(content="*{caret-color:transparent !important}")
    page.wait_for_timeout(350)
    page.evaluate(SETTLE)
    page.wait_for_timeout(150)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path))


def _run_steps(page, steps: str) -> str | None:
    """Runs a scenario inside the page. Returns an error message instead of raising."""
    if not steps.strip():
        return None
    try:
        page.evaluate("async () => {" + JS_HELPERS + steps + "}")
        return None
    except Exception as exc:  # noqa: BLE001
        return re.sub(r"^(Page\.evaluate: )?(Error: )?", "", str(exc).split("\n")[0])[:200]


def _file_url(path: Path, query: str = "") -> str:
    return "file://" + quote(str(path)) + (f"?{query}" if query else "")


# --------------------------------------------------------------------------- #
# Reference
# --------------------------------------------------------------------------- #

def _open_simple_reference(ctx):
    page = ctx.new_page()
    page.clock.set_fixed_time(FIXED_NOW)
    page.goto(_file_url(REFERENCE))
    # The outer "UI Reference" toolbar is not part of the app; and the mock hands out its own arrays
    # by reference, which makes every chat message show twice. A real server returns fresh JSON.
    page.add_style_tag(content=".ref-toolbar{display:none !important}")
    page.evaluate(
        "() => { const m = window.mockApi; window.mockApi = function(){ return JSON.parse(JSON.stringify(m.apply(null, arguments))); }; }"
    )
    return page


def decode_gamified_reference() -> str:
    src = REFERENCE.read_text(encoding="utf-8")
    start = src.index("[", src.index("GAMIFIED_HTML_B64"))
    end = src.index("].join('')", start)
    return base64.b64decode("".join(re.findall(r'"([A-Za-z0-9+/=]+)"', src[start:end]))).decode("utf-8")


def _gamified_reference_page(name: str) -> Path:
    """A copy of the reference app that opens directly on one screen."""
    CACHE.mkdir(parents=True, exist_ok=True)
    doc = decode_gamified_reference()
    first, jump = "(0,l.useState)(`landing`)", "t(`mainmenu`)},[])"
    if doc.count(first) != 1 or doc.count(jump) != 1:
        raise RuntimeError("The reference bundle changed: start-screen anchors not found exactly once.")
    page = CACHE / f"ref-gamified-{name}.html"
    page.write_text(doc.replace(first, f"(0,l.useState)(`{name}`)").replace(jump, f"t(`{name}`)}},[])"), encoding="utf-8")
    return page


def capture_reference(only: str | None) -> dict:
    from playwright.sync_api import sync_playwright

    notes: dict[str, str] = {}
    with sync_playwright() as p:
        browser = _browser(p)
        if only in (None, "simple"):
            for key, _title, steps in SIMPLE:
                ctx = _context(browser)
                page = _open_simple_reference(ctx)
                err = _run_steps(page, steps)
                if err:
                    notes[key] = err
                _settle_and_shoot(page, OUT / "ref" / f"{key}.png")
                ctx.close()
                print("ref ", key, "" if not err else f"(!) {err}", flush=True)
        if only in (None, "gamified"):
            for key, name in GAMIFIED:
                ctx = _context(browser)
                page = ctx.new_page()
                page.clock.install(time=FIXED_NOW)
                page.goto(_file_url(_gamified_reference_page(name), "" if name in NO_PLAYER else "student_id=demo@example.com"))
                page.clock.run_for(12000)         # let typewriter text and mock delays finish
                _settle_and_shoot(page, OUT / "ref" / f"{key}.png")
                ctx.close()
                print("ref ", key, flush=True)
        browser.close()
    return notes


# --------------------------------------------------------------------------- #
# Live app
# --------------------------------------------------------------------------- #

def _bridge_to_reference_mock(live_page, mock_page) -> None:
    """Answer the live page's /api calls with the reference's own mock API."""

    def handle(route, request):
        parts = urlsplit(request.url)
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        try:
            body = request.post_data_json or {}
        except Exception:  # noqa: BLE001
            body = {}
        result = mock_page.evaluate(
            "([p, m, b]) => { try { return {ok: true, data: mockApi(p, m, b)}; } catch (e) { return {ok: false, error: String(e && e.message || e)}; } }",
            [path, request.method, body],
        )
        if result["ok"]:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(result["data"]))
        else:
            route.fulfill(status=400, content_type="application/json", body=json.dumps({"detail": result["error"]}))

    live_page.route("**/api/**", handle)


def capture_live(only: str | None) -> dict:
    from playwright.sync_api import sync_playwright

    notes: dict[str, str] = {}
    with sync_playwright() as p:
        browser = _browser(p)
        if only in (None, "simple"):
            for key, _title, steps in SIMPLE:
                ctx = _context(browser)
                mock_page = _open_simple_reference(ctx)
                page = ctx.new_page()
                page.clock.set_fixed_time(FIXED_NOW)
                _bridge_to_reference_mock(page, mock_page)
                try:
                    page.goto(BASE_URL + "/", wait_until="load")
                    err = _run_steps(page, steps)
                except Exception as exc:  # noqa: BLE001
                    err = "could not open the live app: " + str(exc).split("\n")[0][:160]
                if err:
                    notes[key] = err
                _settle_and_shoot(page, OUT / "live" / f"{key}.png")
                ctx.close()
                print("live", key, "" if not err else f"(!) {err}", flush=True)
        if only in (None, "gamified"):
            ctx = _context(browser)
            page = ctx.new_page()
            rebuilt = False
            try:
                page.goto(BASE_URL + "/gamified/?mock=1", wait_until="load")
                rebuilt = page.locator('meta[name="pixeltutor-build"]').count() > 0
            except Exception as exc:  # noqa: BLE001
                notes["gamified"] = "could not open the live gamified app: " + str(exc).split("\n")[0][:160]
            ctx.close()
            if not rebuilt:
                notes.setdefault("gamified", "not rebuilt yet: the live page is still the old 5-screen version")
                for key, _name in GAMIFIED:
                    (OUT / "live" / f"{key}.png").unlink(missing_ok=True)
                print("live gamified: old page still in place, skipping", flush=True)
            else:
                for key, name in GAMIFIED:
                    ctx = _context(browser)
                    page = ctx.new_page()
                    page.clock.install(time=FIXED_NOW)
                    query = f"mock=1&screen={name}" + ("" if name in NO_PLAYER else "&student_id=demo@example.com")
                    page.goto(f"{BASE_URL}/gamified/?{query}", wait_until="load")
                    page.clock.run_for(12000)
                    _settle_and_shoot(page, OUT / "live" / f"{key}.png")
                    ctx.close()
                    print("live", key, flush=True)
        browser.close()
    return notes


# --------------------------------------------------------------------------- #
# Compare and board
# --------------------------------------------------------------------------- #

def compare(ref: Path, live: Path, diff: Path) -> float:
    """Share of pixels (0..1) that differ by more than TOLERANCE. Also writes a difference image."""
    from PIL import Image, ImageChops

    a, b = Image.open(ref).convert("RGB"), Image.open(live).convert("RGB")
    size = (min(a.width, b.width), min(a.height, b.height))
    a, b = a.crop((0, 0, *size)), b.crop((0, 0, *size))
    r, g, bl = ImageChops.difference(a, b).split()
    strongest = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    mask = strongest.point(lambda v: 255 if v > TOLERANCE else 0)
    changed = mask.histogram()[255]
    dimmed = Image.blend(a, Image.new("RGB", size, (20, 16, 28)), 0.6)
    diff.parent.mkdir(parents=True, exist_ok=True)
    Image.composite(Image.new("RGB", size, (255, 40, 200)), dimmed, mask).save(diff)
    return changed / (size[0] * size[1])


def build(notes: dict) -> dict:
    rows, scores = [], {}
    for key, title in [(k, t) for k, t, _ in SIMPLE] + [(k, n) for k, n in GAMIFIED]:
        ref, live, diff = OUT / "ref" / f"{key}.png", OUT / "live" / f"{key}.png", OUT / "diff" / f"{key}.png"
        score = None
        if ref.exists() and live.exists():
            score = compare(ref, live, diff)
            scores[key] = round(score, 5)
        else:
            diff.unlink(missing_ok=True)
        rows.append((key, title, ref.exists(), live.exists(), score, notes.get(key)))

    def status(score):
        if score is None:
            return "todo", "not built yet"
        if score <= MATCH:
            return "match", f"match · {score * 100:.2f}% differs"
        if score <= CLOSE:
            return "close", f"close · {score * 100:.1f}% differs"
        return "diff", f"different · {score * 100:.0f}% differs"

    def card(key, title, has_ref, has_live, score, note):
        cls, label = status(score)
        cell = lambda folder, ok, alt: (
            f'<a href="{folder}/{key}.png"><img loading="lazy" src="{folder}/{key}.png" alt="{alt}"></a>' if ok else f'<div class="empty">{alt}</div>'
        )
        note_html = f'<div class="note">⚠ {html.escape(note)}</div>' if note else ""
        return (
            f'<section class="row"><header><h3>{html.escape(title)}</h3><span class="chip {cls}">{label}</span></header>{note_html}'
            f'<div class="three"><figure>{cell("ref", has_ref, "no reference capture")}<figcaption>Reference</figcaption></figure>'
            f'<figure>{cell("live", has_live, "not built yet")}<figcaption>Live app</figcaption></figure>'
            f'<figure>{cell("diff", score is not None, "nothing to compare yet")}<figcaption>Difference (pink = differs)</figcaption></figure></div></section>'
        )

    def section(name, prefix):
        part = [r for r in rows if r[0].startswith(prefix)]
        done = sum(1 for r in part if r[4] is not None and r[4] <= MATCH)
        close = sum(1 for r in part if r[4] is not None and MATCH < r[4] <= CLOSE)
        return f"<h2>{name} <small>{done} of {len(part)} match · {close} close</small></h2>" + "".join(card(*r) for r in part)

    total_match = sum(1 for r in rows if r[4] is not None and r[4] <= MATCH)
    extra = f'<p class="note">⚠ {html.escape(notes["gamified"])}</p>' if notes.get("gamified") else ""
    page = f"""<!doctype html><meta charset="utf-8"><title>AI Tutor progress board</title>
<style>
 body{{font-family:system-ui,sans-serif;margin:24px;background:#16131c;color:#eee}}
 h1{{margin:0 0 4px}} h2{{margin:34px 0 10px}} h2 small{{font-weight:400;color:#a99fbd;font-size:15px;margin-left:8px}}
 p{{color:#aaa;margin:0 0 6px}} .big{{font-size:20px;color:#fff;margin:10px 0 2px}}
 .row{{background:#221d2b;border:1px solid #3a3347;border-radius:10px;padding:12px 14px;margin:0 0 14px}}
 .row header{{display:flex;align-items:center;gap:12px;margin-bottom:8px}} h3{{margin:0;font-size:16px}}
 .three{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}} figure{{margin:0}}
 img{{width:100%;display:block;border-radius:6px;border:1px solid #3a3347}}
 figcaption{{font-size:12px;color:#a99fbd;padding-top:5px}}
 .empty{{aspect-ratio:1440/900;display:grid;place-items:center;border:1px dashed #4a4260;border-radius:6px;color:#8d83a3;font-size:13px}}
 .chip{{font-size:12px;padding:3px 10px;border-radius:999px;font-weight:600}}
 .match{{background:#1f5f3a;color:#bff5d0}} .close{{background:#6b5310;color:#ffe9a8}}
 .diff{{background:#6d2130;color:#ffc9d2}} .todo{{background:#3a3347;color:#c9c0da}}
 .note{{color:#ffcf8a;font-size:13px;margin:0 0 8px}}
</style>
<h1>AI Tutor progress board</h1>
<p>Your UI reference next to the live app, screen by screen, fed the same data. Updated {time.strftime('%d %b %Y, %H:%M')}.</p>
<p class="big">{total_match} of {len(rows)} screens match the reference</p>
<p>Match means at most {MATCH * 100:.1f}% of pixels differ. Click any picture to enlarge it.</p>{extra}
{section("Simple dashboard (Mentora)", "simple-")}
{section("Gamified dashboard (PixelTutor)", "gamified-")}
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "scores.json").write_text(json.dumps({"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "match": total_match, "total": len(rows), "scores": scores, "notes": notes}, indent=2))
    print(f"board: {OUT / 'index.html'}  ({total_match} of {len(rows)} match)")
    return scores


def _load_notes() -> dict:
    try:
        return json.loads((OUT / "scores.json").read_text()).get("notes", {})
    except Exception:  # noqa: BLE001
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Reference vs live app, screen by screen.")
    ap.add_argument("what", choices=["ref", "live", "build", "all"])
    ap.add_argument("--only", choices=["simple", "gamified"])
    args = ap.parse_args()
    if not REFERENCE.exists():
        print(f"UI reference not found at {REFERENCE} (set UI_REFERENCE).", file=sys.stderr)
        return 2
    notes = _load_notes()
    if args.what in ("ref", "all"):
        capture_reference(args.only)
    if args.what in ("live", "all"):
        live_notes = capture_live(args.only)
        prefix = {"simple": "simple", "gamified": "gamified"}.get(args.only or "", "")
        notes = {k: v for k, v in notes.items() if prefix and not k.startswith(prefix)} | live_notes
    build(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
