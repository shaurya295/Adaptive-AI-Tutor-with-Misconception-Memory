// Mock backend from the UI reference: every call resolves locally after a short delay.
// Stage 3 replaces these with real API calls of the same shape.

export const delay = (e = 300) => new Promise(t => setTimeout(t, e));
export const todayIso = () => new Date().toISOString().slice(0, 10);
export const daysFromNowIso = e => new Date(Date.now() + e * 864e5).toISOString().slice(0, 10);
export const mockAttempts = [{
  student_id: `demo`,
  concept: `Fractions`,
  question_id: `seed-1`,
  correct: !0,
  time_taken_ms: 4200,
  hint_used: !1
}, {
  student_id: `demo`,
  concept: `Fractions`,
  question_id: `seed-2`,
  correct: !1,
  time_taken_ms: 8100,
  hint_used: !0
}, {
  student_id: `demo`,
  concept: `Algebra`,
  question_id: `seed-3`,
  correct: !0,
  time_taken_ms: 5200,
  hint_used: !1
}, {
  student_id: `demo`,
  concept: `Algebra`,
  question_id: `seed-4`,
  correct: !0,
  time_taken_ms: 3900,
  hint_used: !1
}, {
  student_id: `demo`,
  concept: `Probability`,
  question_id: `seed-5`,
  correct: !1,
  time_taken_ms: 9800,
  hint_used: !1
}];
export async function recordAttempt(e) {
  await delay(150), mockAttempts.push(e);
}
export async function getLearningCurve(e, t = `session`) {
  await delay();
  let n = [];
  for (let e = 0; e < mockAttempts.length; e += 5) {
    let t = mockAttempts.slice(e, e + 5),
      r = t.filter(e => e.correct).length;
    n.push({
      label: `S${Math.floor(e / 5) + 1}`,
      accuracy_pct: Math.round(r / t.length * 1e3) / 10,
      avg_time_ms: Math.round(t.reduce((e, t) => e + t.time_taken_ms, 0) / t.length),
      attempts: t.length
    });
  }
  return n;
}
export async function getRollingStats(e) {
  await delay();
  let t = mockAttempts.slice(-20),
    n = t.filter(e => e.correct).length;
  return {
    rolling_accuracy: Math.round(n / t.length * 1e3) / 10,
    rolling_avg_time_ms: Math.round(t.reduce((e, t) => e + t.time_taken_ms, 0) / t.length),
    streak: 3
  };
}
export const mockHintsByConcept = {
  Fractions: `You're on the right track! When adding fractions, remember the denominators need to match first — what's the smallest number both denominators divide into evenly?`,
  Probability: `Think about it as a fraction: how many outcomes give you what you want, out of all the outcomes that could happen?`,
  Algebra: `Try isolating x on one side — whatever you do to one side of the equation, do to the other.`,
  Geometry: `Picture the shape and count carefully — sometimes it helps to sketch it out.`,
  "Decimals and Percentages": `Remember: percent means 'per hundred' — multiply the decimal by 100 to convert.`
};
export async function getHint(e) {
  return await delay(700), {
    hint_text: mockHintsByConcept[e.concept] || `Take another look at the question — check each option carefully against what you know.`,
    error_type: `Conceptual`,
    recommended_strategy: `small_clue`,
    missing_prerequisite: null
  };
}
export const mockPrerequisites = {
  Fractions: [`Comparing Unit Fractions`, `Common Denominators`],
  Algebra: [`Fractions`, `Arithmetic Operations`],
  "Decimals and Percentages": [`Fractions`],
  Probability: [`Fractions`],
  Geometry: [`Arithmetic Operations`]
};
export const mockMastery = {
  Fractions: .45,
  "Comparing Unit Fractions": .55,
  "Common Denominators": .28,
  Algebra: .45,
  "Arithmetic Operations": .81,
  Probability: .55,
  Geometry: .3,
  "Decimals and Percentages": .67
};
export async function getConceptGraph(e, t) {
  await delay();
  let n = mockPrerequisites[e] || [];
  return {
    nodes: [{
      name: e,
      mastery: mockMastery[e] ?? .4,
      is_focus: !0
    }, ...n.map(e => ({
      name: e,
      mastery: mockMastery[e] ?? .4,
      is_focus: !1
    }))],
    edges: n.map(t => ({
      from: e,
      to: t
    })),
    neo4j_available: !0
  };
}
export async function getProfile(e) {
  return await delay(), {
    profile: {
      student_id: e,
      concept_mastery: {
        Fractions: {
          mastery: .45,
          consecutive_misses: 0,
          next_review: todayIso(),
          last_practiced: todayIso()
        },
        Algebra: {
          mastery: .6,
          consecutive_misses: 1,
          next_review: daysFromNowIso(3),
          last_practiced: todayIso()
        }
      },
      weak_prerequisites: [`Common Denominators`],
      recent_attempts: [{
        concept: `Fractions`,
        correct: !0
      }, {
        concept: `Algebra`,
        correct: !1
      }, {
        concept: `Algebra`,
        correct: !0
      }]
    },
    due_for_review: [`Fractions`]
  };
}
