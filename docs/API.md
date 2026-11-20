# API

All endpoints are JSON, under `/api`, served by `./run.sh real` at `http://127.0.0.1:8000`.

**Interactive docs:** `http://127.0.0.1:8000/docs` lists every route with its exact request and response schema, generated from the code.

**Errors:** `{"detail": "..."}` with these status codes:

| Code | Meaning |
|---|---|
| 400 | Bad input |
| 401 | Not signed in |
| 402 | Not enough coins |
| 403 | Not allowed |
| 404 | Not found |
| 503 | The AI model is unavailable. The answer was not marked. |

## Signing in

Sign-in is by email (or a hero name in the game). The server then sets an HttpOnly session cookie, `tutor_session`, which identifies the caller on every later request.

The `student_id` parameters below are optional:
- **A student** may only name themselves (403 otherwise), and defaults to themselves when it's left out.
- **A teacher** may name any student.

| Method | Path | Body / query | Returns |
|---|---|---|---|
| POST | `/api/login` | `{email}` | `{student_id, role}` (role is `teacher` for configured school domains or addresses) |
| POST | `/api/logout` | – | `{ok}` |
| POST | `/api/auth/guest` | `{name}` | `{student_id, role, display_name}` (the game's hero-name sign-in) |
| GET | `/api/me` | `?concept` | `{student_id, role, display_name, companion_id, hud, due_count}` |
| PATCH | `/api/me` | `{display_name?, companion_id?}` | same as GET |

`hud` = `{level, xp, xp_pct, coins, streak, hearts, max_hearts, badges[]}`

## Student: tutoring and quizzes (Simple dashboard)

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | `/api/state` | `?concept` | `{messages, profile, active_question, pre_test_scores, post_test_scores, due_for_review, hint_ladder}` |
| POST | `/api/chat` | `{concept, message, explain_only?}` | `{reply, active_question, hint_ladder, profile, escalated}` |
| POST | `/api/quiz/start` | `{concept, variant: pre\|post}` | `{questions: [{question_id, question, choices}]}` (never the answers) |
| POST | `/api/quiz/skip` | `{concept, variant}` | `{ok}` |
| POST | `/api/quiz/submit` | `{concept, variant, selected_indices}` | `{correct, total}` |
| GET | `/api/profile` | `?student_id` | `{profile, due_for_review}` |
| GET | `/api/schedule` | `?student_id` | `{schedule: [...]}` |

`profile.concept_mastery[topic]` = `{mastery, consecutive_misses, next_review, last_practiced}`

`hint_ladder` is one of:
- `{kind: none}`
- `{kind: steps, current_index, labels}`
- `{kind: note, text}`

**How `/api/chat` behaves:**
- **No problem open for the topic:** explains, then sets a practice problem from the bank.
- **A problem is open:** grades the message as an answer and climbs the hint ladder.
- **`explain_only: true`:** only explains. It never opens or grades a problem; the game's Free Quest uses this.

## Game (PixelTutor)

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | `/api/game/quiz` | `?variant=pre\|post` | one question per topic, without answers |
| GET | `/api/game/lesson` | `?concept` (optional) | `{concept, reason, lesson_index, lesson_total, dialog[5], questions}` (without a concept, picks a topic due for review, otherwise the weakest) |
| POST | `/api/game/sessions` | `{kind: pretest\|lesson\|posttest, concept?}` | `{session_id}` |
| POST | `/api/game/sessions/{id}/finish` | – | `{questions, correct, xp_earned, coins_earned, duration_s, hud}` |
| POST | `/api/game/answer` | `{question_id, selected_index (null = time ran out), time_taken_ms?, session_id?}` | `{correct, correct_index, feedback, misconception_id, misconception, seen_before, xp_delta, coins_delta, escalated, new_badges, mastery, hud}` |
| POST | `/api/game/hint` | `{question_id}` | `{clue, hud}` (costs 5 coins once per question; 402 if short) |
| GET | `/api/game/curve` | `?granularity=session\|day` | `{points: [{label, accuracy_pct, avg_time_ms, attempts}]}` |
| GET | `/api/game/stats` | – | rolling accuracy, previous accuracy, average time, hint usage, active misconceptions, escalations, streak, lesson progress, average confidence |
| GET | `/api/game/leaderboard` | `?window=7d\|all` | `{entries: [{rank, name, xp, streak, badge, avatar, is_me}]}` (other students' ids are never sent) |

Game rules (XP, levels, coins, hearts, streaks, badges) are in `backend/game.py`. Three wrong answers in a row on a topic notify the teacher and refill the hearts.

## Teacher

| Method | Path | Body / query | Returns |
|---|---|---|---|
| GET | `/api/eval-metrics` | `?student_id` (none = whole class) | six metrics: `[{label, display, status, description}]` |
| GET | `/api/misconception-graph` | `?concept&student_id` | `{nodes: [{name, mastery, is_focus}], edges: [{from, to}], neo4j_available}` |
| GET | `/api/escalations` | `?student_id` | `{escalations: [{id, time, topic, trigger, misses, trigger_type, warranted}]}` (teacher-only) |
| POST | `/api/escalations/review` | `{id, warranted}` | `{ok}` (teacher-only) |
| GET | `/api/memory-impact` | `?student_id` | `{available, concept, misconception, first, later}` (a student's first miss with no history next to a later miss on the same gap; teacher-only) |
