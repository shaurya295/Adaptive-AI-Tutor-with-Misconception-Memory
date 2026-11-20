# Adaptive AI Tutor with Misconception Memory

A maths tutor that remembers *why* each student gets things wrong, and adapts to it.
It began as a hackathon-winning project at the IIT Mandi Himshikhar AI & ML programme and has since been rebuilt into a complete, tested app.

- **Two dashboards, one student record.**
  - **Mentora:** a calm "Simple" dashboard with a chat tutor.
  - **PixelTutor:** a retro "Gamified" dashboard with lessons, XP, coins, hearts, badges and a leaderboard.
  - Progress made in one shows up in the other.
- **Misconception memory.** Every wrong answer is tied to a named misconception from the curriculum, such as "adds the tops and the bottoms". The tutor brings up a gap the student has shown before.
- **A hint ladder.** After a miss the tutor gives a small clue, then a stronger hint, then a worked example. A careless slip only gets a "recheck this step" nudge.
- **Teacher view.** Teachers can see:
  - each student's mastery and weak prerequisites;
  - six evaluation metrics;
  - the prerequisite graph;
  - an escalation feed, raised after repeated misses, distress, or replies typed faster than a person can write them;
  - real before/after examples of what the memory changed.
- **Runs on a laptop.** A small local model (`gemma4:e2b` through Ollama) writes explanations and hints. Quizzes, the game and clearly right answers are graded instantly without the model.

## Quick start (Ubuntu)

You need Python 3.11+, [Ollama](https://ollama.com) and Google Chrome. Node.js is only needed to change the gamified dashboard.

```bash
sudo apt install -y python3-venv          # once
ollama pull gemma4:e2b                    # the tutor's model (4.6 GB)
ollama pull nomic-embed-text              # curriculum search (274 MB)

git clone https://github.com/shaurya295/Adaptive-AI-Tutor-with-Misconception-Memory.git
cd Adaptive-AI-Tutor-with-Misconception-Memory
./run.sh setup                            # virtualenv, Python packages, .env
./run.sh doctor                           # checks everything and says how to fix anything missing
./run.sh real                             # starts the app
```

Open **http://127.0.0.1:8000** and sign in with an email:
- **Personal address** (e.g. `you@gmail.com`): opens the student side. Choose 📓 Simple or 🕹️ Gamified.
- **School address** (e.g. `teacher@school.edu`): opens the teacher dashboard. Which domains count as school is set in `.env`.

Keep the terminal open while you use the app. **Ctrl + C** stops it.

No Ollama? Run `TUTOR_LLM=fake ./run.sh real` to try everything with canned tutor replies.

### All commands

| Command | Does |
|---|---|
| `./run.sh setup [--dev]` | Creates `.venv`, installs packages (`--dev` adds the test tools), copies `.env.example` to `.env` |
| `./run.sh real [--port 8010]` | Starts the app |
| `./run.sh doctor [--dev]` | Checks Python, packages, Ollama, models, memory and port, and prints the fix for anything wrong |
| `./run.sh test` | Runs the automated tests (no model needed) |
| `./run.sh board` | Captures every screen of the app next to the original UI design and scores the difference (start the app first; needs `--dev` setup) |
| `./run.sh bench <model>` | Measures speed, memory and judging accuracy of a model on this machine |

Changing the gamified dashboard: `cd frontend_src/gamified && npm install && npm run dev`. It rebuilds into `frontend_web/gamified/` on every save, and the built files are committed, so Node isn't needed just to run the app.

## How it works

```
Browser ── Mentora (frontend_web/simple)    ┐
        └─ PixelTutor (frontend_web/gamified)┴─▶ FastAPI (backend/api) ─▶ SQLite (backend/data)
                                                    │
                     chat turn ─▶ LangGraph agents ─┤─▶ Ollama (gemma4:e2b)
                     quiz / game answer ─▶ answer key + misconception tags (no model)
```

**A tutoring turn** (`backend/agents/orchestrator.py`):
1. **Evaluator:** checks a bare answer (`3/4`, `0.75`, `x = 4`) against the answer key, with no model call. Anything else gets one short model call that returns the verdict and the diagnosis together. It also flags replies typed faster than a person can write.
2. **Diagnostic:** decides careless vs. misunderstanding vs. missing prerequisite. For number answers this is decided in code, because small models call almost everything "careless". It then picks the next step on the hint ladder by rule.
3. **Tutor Planner:** writes the hint (one model call), grounded in the curriculum. An answer-leak guard checks it against the key: a leaking hint is rewritten once, then swapped for a hand-written one.
4. **Escalation:** after repeated misses, distress or a cheating flag, it tells the teacher, with a summary built from the turn's facts.
5. **Memory update:** adjusts mastery, the miss streak, weak prerequisites, the spaced-review date and the turn log.

| Part | Where |
|---|---|
| API (sign-in, tutoring, quizzes, teacher views) | `backend/api/server.py`, `backend/api/auth.py` |
| Game API (lessons, answers, hints, HUD, leaderboard) | `backend/api/game_routes.py`, rules in `backend/game.py` |
| Agents | `backend/agents/` |
| The one connection to the model | `backend/llm.py` |
| Answer matching (fractions, decimals, percentages, units) | `backend/grading.py` |
| Memory: mastery, sessions, turns, quizzes, game | `backend/memory/` (SQLite via SQLAlchemy) |
| Content: questions, lessons, 26 misconceptions, prerequisite graph | `backend/content/` |
| Curriculum notes for hints (searched with Chroma) | `backend/curriculum/`, `backend/rag/` |
| Six evaluation metrics | `backend/evals/metrics.py` |
| Simple dashboard | `frontend_web/simple/index.html` |
| Gamified dashboard source (React 19 + Vite) | `frontend_src/gamified/` |

**Speed on a 2-core laptop with `gemma4:e2b`:**

| Action | Time |
|---|---|
| Wrong answer in chat | ~10–15 s |
| Explanation | ~10–20 s |
| Quiz and game answers | instant |

Benchmark another model with `./run.sh bench <model>`.

## Testing

`./run.sh test` runs about 70 tests. They cover:
- answer matching, the hint ladder and the leak guard;
- the game rules, the six metrics and the content packages;
- every API route, including access control (students can only see their own data; teacher-only routes).

A stand-in model is used, so no Ollama is needed. `backend/tools/eval_errors.py` checks the real model's error labelling against a hand-labelled set.

## The design reference and deviations

The interface follows a UI reference made during the hackathon. `./run.sh board` compares every screen against it. Where the app deliberately differs, it's listed with the reason in [`docs/deviations.md`](docs/deviations.md). Examples: bugs in the reference that were fixed, and game mechanics the reference only faked, which are now real.

## More

- [`docs/API.md`](docs/API.md): every endpoint
- [`SECURITY.md`](SECURITY.md): what is protected, and the known limits
- [`docs/deviations.md`](docs/deviations.md): differences from the UI reference

Earlier versions stored memory in Neo4j and had a Streamlit interface. Both were replaced: memory now lives in SQLite, so nothing else needs installing, and the prerequisite graph is a content file (`backend/content/concepts.json`).
