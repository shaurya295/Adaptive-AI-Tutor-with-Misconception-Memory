"""Scripted click-through of the gamified app; prints what each step showed and any page errors."""
import sys
from playwright.sync_api import sync_playwright
errors, seen = [], []
U = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000") + "/gamified/"
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.set_default_timeout(8000)
    pg.on("pageerror", lambda e: errors.append(str(e)[:160]))
    pg.on("console", lambda m: errors.append("console: " + m.text[:160]) if m.type == "error" and "favicon" not in m.text and "404" not in m.text else None)
    text = lambda n=90: (pg.wait_for_timeout(900), pg.locator("body").inner_text().replace("\n", " ")[:n])[1]
    pg.goto(U); pg.click("text=START GAME"); pg.fill("input", "Shaurya"); pg.click("text=YES!")
    seen.append("signed in -> " + text(120).split("82 ", 1)[-1][:20])
    for button in ["HOW IT WORKS", "LEADERBOARD", "PROGRESS", "EVAL METRICS", "MISCONCEPTIONS", "SPACED REVIEW", "SWITCH STUDENT", "FREE QUEST"]:
        pg.goto(U + "?screen=mainmenu&student_id=shaurya@example.com"); pg.wait_for_timeout(400)
        pg.click(f"button:has-text('{button}')"); seen.append(text(60).split("82 ", 1)[-1][:28])
    pg.goto(U + "?screen=pretest&student_id=shaurya@example.com"); pg.wait_for_timeout(3000)
    for _ in range(5):
        pg.locator(".grid button").first.click(); pg.wait_for_timeout(500)
        pg.locator("button:has-text('NEXT'), button:has-text('FINISH')").first.click(); pg.wait_for_timeout(3000)
    seen.append("after pretest -> " + text(140).split("82 ", 1)[-1][:24])
    pg.goto(U + "?screen=freequest&student_id=shaurya@example.com"); pg.wait_for_timeout(500)
    pg.fill("textarea", "What is a fraction?"); pg.click("text=CAST SPELL"); pg.wait_for_timeout(3500)
    seen.append("freequest answered: " + str(pg.locator("text=PIXEL — AI TUTOR").count() > 0))
    pg.goto(U + "?screen=progress&student_id=shaurya@example.com"); pg.wait_for_timeout(1500)
    pg.click("text=CONTINUE"); pg.wait_for_timeout(900); pg.click("text=CLAIM REWARD"); pg.wait_for_timeout(900)
    seen.append("progress -> complete -> reward: " + str(pg.locator("text=GREAT JOB!").count() > 0))
    b.close()
print("\n".join(seen)); print("errors:", errors or "none")
