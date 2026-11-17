# Deviations from the UI reference

The UI reference (`Hackathon IIT Mandi Layout.html`) is the target for how the app looks and
behaves. Where the app deliberately does something different, it is listed here with the reason.
Each entry needs the project owner's sign-off.

| ID | Screen | Reference behaviour | App behaviour | Why | Sign-off |
|---|---|---|---|---|---|
| D1 | Simple · S2 → S3 | "📝 End session — take the post-test" draws the post-test on the Session-end screen but stays on the Tutoring screen, so nothing visible happens until the student clicks "3 Session end". | Switches to the Session-end screen when the post-test starts. | The reference's behaviour leaves the student stuck; the final picture is identical. | approved 2026-11-18 |

| D2 | Simple · T1, T3 subtitles | "…read live from Neo4j by student email…" and "…from the Neo4j REQUIRES graph…" | "…read live from the tutor's memory store…" and "…from the prerequisite graph…" | Memory lives in SQLite and the graph in a content file; the original sentences would be untrue. Changes only the wording on the reference's own mock data, so the board still differs slightly on T1 and T3. | approved 2026-11-18 |
| D3 | Gamified quizzes | The last answer is counted twice at FINISH (5/5 can show 6/5) | Counted once | Bug in the reference. | proposed |


## Gamified dashboard: mechanics the reference shows but never defines (owner's decisions, 2026-11-18)
| ID | Mechanic | Reference | App |
|---|---|---|---|
| G1 | Lives (3 ❤️) | Decoration; "Wrong answers cost one" but they never change | Hearts = wrong answers left on the current topic before the tutor calls the teacher (the real escalation rule). At zero the teacher is notified and hearts refill. No lockout. |
| G2 | Coins | Always 82; "hint coins" and "power-ups" described but not built | Earned for correct answers and finished sessions. Spent on an extra hint before answering. The hint after a wrong answer is always free, so coins never block help. |
| G3 | Leaderboard | 10 made-up players | Real players on this server only, ranked by real XP. |
| G4 | Lesson topic | No topic picker; START LESSON starts | The tutor picks (a topic due for review first, otherwise the weakest). The student can still choose via REVIEW NOW, the misconception map, or the Free Quest chips. |
| G6 | Reward screen | Always "FRACTIONS MASTER" | Shows the latest badge really earned; with none yet, "NEXT BADGE · TOPIC MASTER · Reach 70% mastery in any topic". Proposed by Claude. |
| G7 | Progress tip | "You're on a streak! …PHOENIX badge…" whatever the data | Says the real streak, or how to start one. Proposed by Claude. |
| G5 | Free Quest chips | MATH, SCIENCE, HISTORY, ENGLISH, ART, CODE | Relabelled to the five maths topics plus ANY MATHS (same colours and layout). Proposed by Claude; owner may veto. |


## Decisions that keep the reference as it is
- **T1 schedule table:** the older repo page showed an extra spaced-repetition table on Student lookup. Removed (2026-11-18) to match the reference; next-review dates remain on the student cards and in the due-for-review banner.
- **T5 "Memory made this better":** stays static for now, as the reference marks it Illustrative. **Planned for M3:** make it live (a real student's earlier and later replies for the same misconception).
