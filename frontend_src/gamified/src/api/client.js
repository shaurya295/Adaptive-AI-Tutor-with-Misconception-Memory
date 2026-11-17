// The game's only way to reach data. Each function returns the shape the screens were built
// around (the UI reference's mock), whether the data comes from the server or, with ?mock=1,
// from the reference's own fake backend in ./mock.js.
import * as mock from './mock';
import { POSTTEST_QUESTIONS, PRETEST_QUESTIONS } from '../data/content';
import { setHud } from './hud';
import { isMock } from './mode';

export { isMock };

export class ApiError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}

async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(path, {
    method,
    headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'same-origin',
  });
  let data = null;
  try { data = await res.json(); } catch { /* empty body */ }
  if (!res.ok) throw new ApiError(res.status, (data && data.detail) || `Request failed (${res.status})`);
  if (data && data.hud) setHud(data.hud);
  return data;
}

// ---- identity -------------------------------------------------------------------------

export async function getMe() {
  if (isMock) return null;
  try { const me = await api('/api/me'); setHud(me.hud); return me; }
  catch (e) { if (e.status === 401) return null; throw e; }
}
export const guestSignIn = (name) => (isMock ? Promise.resolve(null) : api('/api/auth/guest', { method: 'POST', body: { name } }));
export const updateMe = (fields) => (isMock ? Promise.resolve(null) : api('/api/me', { method: 'PATCH', body: fields }));
export const signOut = () => (isMock ? Promise.resolve(null) : api('/api/logout', { method: 'POST' }));

// ---- questions and answers ------------------------------------------------------------

const toReferenceShape = (q) => ({ id: q.question_id, concept: q.concept, text: q.question, options: q.choices, correct: null });

export async function loadQuiz(variant) {
  if (isMock) return variant === 'pre' ? PRETEST_QUESTIONS : POSTTEST_QUESTIONS;
  const data = await api(`/api/game/quiz?variant=${variant}`);
  return data.questions.map(toReferenceShape);
}

export async function loadLesson(concept) {
  const data = await api('/api/game/lesson' + (concept ? `?concept=${encodeURIComponent(concept)}` : ''));
  return { ...data, questions: data.questions.map(toReferenceShape) };
}

export const startSession = (kind, concept) =>
  isMock ? Promise.resolve({ session_id: null }) : api('/api/game/sessions', { method: 'POST', body: { kind, concept } });

let lastSummary = null;
export const getLastSummary = () => lastSummary;
export async function finishSession(sessionId) {
  if (isMock || sessionId == null) return null;
  lastSummary = await api(`/api/game/sessions/${sessionId}/finish`, { method: 'POST' });
  return lastSummary;
}

// Grades one answer. `picked` is the option text, or null when time ran out.
// Resolves to {correct, correctAnswer, feedback, escalated, newBadges}.
export async function answerQuestion(question, picked, timeTakenMs, sessionId, studentId) {
  if (isMock) {
    const correct = picked === question.correct;
    mock.recordAttempt({ student_id: studentId || 'anonymous', concept: question.concept, question_id: question.id, correct, time_taken_ms: timeTakenMs, hint_used: false });
    let feedback = null;
    if (!correct) {
      feedback = (await mock.getHint({ student_id: studentId || 'anonymous', concept: question.concept, question: question.text,
        student_answer: picked ?? '(no answer — time ran out)', correct_answer: question.correct })).hint_text;
    }
    return { correct, correctAnswer: question.correct, feedback, escalated: false, newBadges: [] };
  }
  const index = picked == null ? null : question.options.indexOf(picked);
  const res = await api('/api/game/answer', { method: 'POST', body: { question_id: question.id, selected_index: index, time_taken_ms: timeTakenMs, session_id: sessionId } });
  let feedback = res.feedback;
  if (feedback && res.seen_before) feedback += ' (This is a mix-up you have made before; it is worth slowing down here.)';
  if (res.escalated) feedback = (feedback ? feedback + ' ' : '') + "That's three in a row, so I've asked your teacher to go through this topic with you. Your hearts are refilled.";
  return { correct: res.correct, correctAnswer: question.options[res.correct_index], feedback, escalated: res.escalated, newBadges: res.new_badges };
}

export const buyHint = (questionId) => api('/api/game/hint', { method: 'POST', body: { question_id: questionId } });

// ---- progress views (same shapes as the reference's mock) -----------------------------

export async function getLearningCurve(studentId, granularity = 'session') {
  if (isMock) return mock.getLearningCurve(studentId, granularity);
  return (await api(`/api/game/curve?granularity=${granularity}`)).points;
}
export async function getRollingStats(studentId) {
  if (isMock) return mock.getRollingStats(studentId);
  const s = await api('/api/game/stats');
  return { ...s, rolling_accuracy: s.rolling_accuracy ?? 0, rolling_avg_time_ms: s.rolling_avg_time_ms ?? 0 };
}
export const getStats = () => api('/api/game/stats');
export async function getConceptGraph(concept, studentId) {
  if (isMock) return mock.getConceptGraph(concept, studentId);
  return api(`/api/misconception-graph?concept=${encodeURIComponent(concept)}`);
}
export async function getProfile(studentId) {
  if (isMock) return mock.getProfile(studentId);
  return api('/api/profile');
}
export const getLeaderboard = (window = 'all') => api(`/api/game/leaderboard?window=${window}`);

// Free Quest: ask the tutor anything; the answer is an explanation, never a graded problem.
export async function askTutor(concept, question) {
  const res = await api('/api/chat', { method: 'POST', body: { concept, message: question, explain_only: true } });
  return res.reply.replace(/\*\*/g, '');
}
