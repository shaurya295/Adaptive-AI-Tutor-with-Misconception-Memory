# Deviations from the UI reference

The UI reference (`Hackathon IIT Mandi Layout.html`) is the target for how the app looks and
behaves. Where the app deliberately does something different, it is listed here with the reason.
Each entry needs the project owner's sign-off.

| ID | Screen | Reference behaviour | App behaviour | Why | Sign-off |
|---|---|---|---|---|---|
| D1 | Simple · S2 → S3 | "📝 End session — take the post-test" draws the post-test on the Session-end screen but stays on the Tutoring screen, so nothing visible happens until the student clicks "3 Session end". | Switches to the Session-end screen when the post-test starts. | The reference's behaviour leaves the student stuck; the final picture is identical. | approved 2026-11-18 |
| D2 | Simple · T1, T3 subtitles | "…read live from Neo4j by student email…" and "…from the Neo4j REQUIRES graph…" | "…read live from the tutor's memory store…" and "…from the prerequisite graph…" | Memory lives in SQLite and the graph in a content file; the original sentences would be untrue. Changes only the wording on the reference's own mock data, so the board still differs slightly on T1 and T3. | approved 2026-11-18 |
| D3 | Gamified quizzes | The last answer is counted twice at FINISH (5/5 can show 6/5) | Counted once | Bug in the reference. | approved 2026-11-21 |
| D4 | Gamified animations | Seven animations are used but never defined (blink, twinkle, clouds, bus, walk-in, confetti, glitch), so they stay frozen; the leaderboard ticker reuses the cloud animation | All seven defined in `styles/fixes.css`, first frame equal to the static picture; the ticker scrolls with its own animation. On the board, animated text is drawn on its own layer, so letter edges differ slightly (How it works 0.71%, leaderboard 0.59%, others under 0.5%); nothing moves or changes colour. | Bug in the reference. | approved 2026-11-21 |
| D5 | Gamified onboarding | Welcome and Choose-your-avatar screens can't be reached (the menu has no way in) | A new player goes sign-in → Welcome → Avatar → How it works → pre-test; returning players go to the menu. | Unreachable screens in the reference. | approved 2026-11-21 |
| D6 | Gamified post-test | "▶ CLAIM REWARD" after the learning-gain view does nothing | Opens the session summary, whose own CLAIM REWARD leads to the reward screen. | Dead button in the reference. | approved 2026-11-21 |


## Gamified dashboard: mechanics the reference shows but never defines (owner's decisions, 2026-11-18)
| ID | Mechanic | Reference | App |
|---|---|---|---|
| G1 | Lives (3 ❤️) | Decoration; "Wrong answers cost one" but they never change | Hearts = wrong answers left on the current topic before the tutor calls the teacher (the real escalation rule). At zero the teacher is notified and hearts refill. No lockout. |
| G2 | Coins | Always 82; "hint coins" and "power-ups" described but not built | Earned for correct answers and finished sessions. Spent on an extra hint before answering. The hint after a wrong answer is always free, so coins never block help. |
| G3 | Leaderboard | 10 made-up players | Real players on this server only, ranked by real XP. |
| G4 | Lesson topic | No topic picker; START LESSON starts | The tutor picks (a topic due for review first, otherwise the weakest). The student can still choose via REVIEW NOW, the misconception map, or the Free Quest chips. |
| G6 | Reward screen | Always "FRACTIONS MASTER" | Shows the latest badge really earned; with none yet, "NEXT BADGE · TOPIC MASTER · Reach 70% mastery in any topic". Approved by the owner 2026-11-21. |
| G7 | Progress tip | "You're on a streak! …PHOENIX badge…" whatever the data | Says the real streak, or how to start one. Approved by the owner 2026-11-21. |
| G8 | Switch student | Lists every player made on the device and switches between them | Shows the signed-in player; ➕ ADD NEW PLAYER signs out and starts a new hero. Guest players have no password, so switching into someone else's account would let anyone on the laptop use it. Approved by the owner 2026-11-21. |
| G9 | Eval metrics (game) | Fixed numbers, "CONFIDENCE … trend upward" | The player's own numbers; confidence comes from tutor chats (the game's multiple-choice answers do not measure it), shown as — until there is a chat. Approved by the owner 2026-11-21. |
| G5 | Free Quest chips | MATH, SCIENCE, HISTORY, ENGLISH, ART, CODE | Relabelled to the five maths topics plus ANY MATHS (same colours and layout). Approved by the owner 2026-11-21. |


## Decisions that keep the reference as it is
- **T1 schedule table:** the older repo page showed an extra spaced-repetition table on Student lookup. Removed (2026-11-18) to match the reference; next-review dates remain on the student cards and in the due-for-review banner.
- **T5 "Memory made this better":** stays static for now, as the reference marks it Illustrative. **Planned for M3:** make it live (a real student's earlier and later replies for the same misconception).
