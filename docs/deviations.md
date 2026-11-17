# Deviations from the UI reference

The UI reference (`Hackathon IIT Mandi Layout.html`) is the target for how the app looks and
behaves. Where the app deliberately does something different, it is listed here with the reason.
Each entry needs the project owner's sign-off.

| ID | Screen | Reference behaviour | App behaviour | Why | Sign-off |
|---|---|---|---|---|---|
| D1 | Simple · S2 → S3 | "📝 End session — take the post-test" draws the post-test on the Session-end screen but stays on the Tutoring screen, so nothing visible happens until the student clicks "3 Session end". | Switches to the Session-end screen when the post-test starts. | The reference's behaviour leaves the student stuck; the final picture is identical. | approved 2026-11-18 |

| D2 | Simple · T1, T3 subtitles | "…read live from Neo4j by student email…" and "…from the Neo4j REQUIRES graph…" | "…read live from the tutor's memory store…" and "…from the prerequisite graph…" | Memory lives in SQLite and the graph in a content file; the original sentences would be untrue. Changes only the wording on the reference's own mock data, so the board still differs slightly on T1 and T3. | approved 2026-11-18 |

## Decisions that keep the reference as it is
- **T1 schedule table:** the older repo page showed an extra spaced-repetition table on Student lookup. Removed (2026-11-18) to match the reference; next-review dates remain on the student cards and in the due-for-review banner.
- **T5 "Memory made this better":** stays static for now, as the reference marks it Illustrative. **Planned for M3:** make it live (a real student's earlier and later replies for the same misconception).
