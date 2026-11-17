# Deviations from the UI reference

The UI reference (`Hackathon IIT Mandi Layout.html`) is the target for how the app looks and
behaves. Where the app deliberately does something different, it is listed here with the reason.
Each entry needs the project owner's sign-off.

| ID | Screen | Reference behaviour | App behaviour | Why | Sign-off |
|---|---|---|---|---|---|
| D1 | Simple · S2 → S3 | "📝 End session — take the post-test" draws the post-test on the Session-end screen but stays on the Tutoring screen, so nothing visible happens until the student clicks "3 Session end". | Switches to the Session-end screen when the post-test starts. | The reference's behaviour leaves the student stuck; the final picture is identical. | pending |

## Proposed, not yet applied
- **Neo4j wording.** T1 says "Mastery and prerequisites are read live from Neo4j by student email"; T3 says "Prerequisite structure from the Neo4j REQUIRES graph". The app now keeps memory in SQLite and the graph in a content file. Proposal: "read live from the tutor's memory store" and "from the prerequisite graph".
- **T1 schedule table.** The repo's Simple page shows a spaced-repetition schedule table on T1 that the reference does not have. It is visible only on real data (not on the board). Keep or remove.
- **T5 "Memory made this better"** is marked Illustrative in the reference and stays static for now.
