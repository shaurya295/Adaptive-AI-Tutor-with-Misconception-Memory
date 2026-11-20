// Fixed content and small helpers used by the screens.

export const COMPANIONS = [{
  id: `wizard`,
  emoji: `🧙`,
  name: `WIZARD`,
  color: `#ff00cc`,
  desc: `Magic & Science`
}, {
  id: `knight`,
  emoji: `⚔️`,
  name: `KNIGHT`,
  color: `#ff8c1a`,
  desc: `History & Logic`
}, {
  id: `ranger`,
  emoji: `🏹`,
  name: `RANGER`,
  color: `#4aff91`,
  desc: `Nature & Bio`
}, {
  id: `scholar`,
  emoji: `📚`,
  name: `SCHOLAR`,
  color: `#00ffee`,
  desc: `Literature & Art`
}, {
  id: `inventor`,
  emoji: `⚙️`,
  name: `INVENTOR`,
  color: `#ffe94a`,
  desc: `Tech & Math`
}];
export const HOW_IT_WORKS = [{
  icon: `🎯`,
  color: `#ff00cc`,
  title: `QUEST`,
  text: `Answer questions to complete lesson quests and earn XP!`
}, {
  icon: `🪙`,
  color: `#ffe94a`,
  title: `COINS`,
  text: `Correct answers = coins. Use them to unlock power-ups!`
}, {
  icon: `💡`,
  color: `#00ffee`,
  title: `HINTS`,
  text: `Stuck? Use a hint coin to get a clue from Pixel!`
}, {
  icon: `❤️`,
  color: `#ff3355`,
  title: `LIVES`,
  text: `You have 3 lives per session. Wrong answers cost one!`
}, {
  icon: `🏆`,
  color: `#4aff91`,
  title: `REWARDS`,
  text: `Complete sessions to unlock trophies and level badges!`
}];
export const PRETEST_QUESTIONS = [{
  id: `pre-q1`,
  text: `Which is greater: 3/4 or 5/8?`,
  options: [`3/4`, `5/8`, `They're equal`, `Cannot tell`],
  correct: `3/4`,
  concept: `Fractions`
}, {
  id: `pre-q2`,
  text: `A fair coin is flipped once. What is the probability of heads?`,
  options: [`1/4`, `1/3`, `1/2`, `1`],
  correct: `1/2`,
  concept: `Probability`
}, {
  id: `pre-q3`,
  text: `Solve for x: x + 5 = 12`,
  options: [`5`, `7`, `17`, `6`],
  correct: `7`,
  concept: `Algebra`
}, {
  id: `pre-q4`,
  text: `How many degrees are in a triangle's interior angles combined?`,
  options: [`90`, `180`, `270`, `360`],
  correct: `180`,
  concept: `Geometry`
}, {
  id: `pre-q5`,
  text: `Convert 0.5 to a percentage.`,
  options: [`5%`, `50%`, `0.5%`, `500%`],
  correct: `50%`,
  concept: `Decimals and Percentages`
}];
export const LESSON_QUESTION = [{
  id: `les-q1`,
  text: `What is 1/2 + 1/4?`,
  options: [`2/6`, `3/4`, `1/4`, `2/4`],
  correct: `3/4`,
  concept: `Fractions`
}];
export const POSTTEST_QUESTIONS = [{
  id: `post-q1`,
  text: `Which is greater: 2/3 or 5/9?`,
  options: [`5/9`, `2/3`, `They're equal`, `Cannot tell`],
  correct: `2/3`,
  concept: `Fractions`
}, {
  id: `post-q2`,
  text: `A fair coin is flipped once. What is the probability of tails?`,
  options: [`1/3`, `1/2`, `1/4`, `1`],
  correct: `1/2`,
  concept: `Probability`
}, {
  id: `post-q3`,
  text: `Solve for x: x - 4 = 9`,
  options: [`5`, `13`, `36`, `9`],
  correct: `13`,
  concept: `Algebra`
}, {
  id: `post-q4`,
  text: `How many degrees are in a right angle?`,
  options: [`45`, `90`, `180`, `360`],
  correct: `90`,
  concept: `Geometry`
}, {
  id: `post-q5`,
  text: `Convert 0.25 to a percentage.`,
  options: [`2.5%`, `0.25%`, `25%`, `250%`],
  correct: `25%`,
  concept: `Decimals and Percentages`
}];
export const LESSON_SCRIPT = [`Welcome to today's lesson! Today we're covering Fractions. Ready?`, `A fraction is a part of a whole — the bottom number (denominator) says how many equal pieces the whole is split into.`, `To ADD two fractions, they need the same denominator first — that's called a common denominator.`, `Once the denominators match, just add the top numbers (numerators) and keep the denominator the same!`, `Now let's test your knowledge with a quick question...`];
export const QUEST_CATEGORIES = [{
  label: `∑ MATH`,
  color: `#ff00cc`
}, {
  label: `⚗ SCIENCE`,
  color: `#00ffee`
}, {
  label: `📜 HISTORY`,
  color: `#ff8c1a`
}, {
  label: `📖 ENGLISH`,
  color: `#4aff91`
}, {
  label: `🎨 ART`,
  color: `#ff4fa3`
}, {
  label: `💻 CODE`,
  color: `#ffe94a`
}];
export const LEADERBOARD = [{
  rank: 1,
  name: `QUANTUMKID`,
  xp: 12400,
  streak: 21,
  badge: `🔥`,
  avatar: `🧙`
}, {
  rank: 2,
  name: `PRIYA_STAR`,
  xp: 11200,
  streak: 18,
  badge: `⭐`,
  avatar: `📚`
}, {
  rank: 3,
  name: `ALEXDOOM`,
  xp: 10800,
  streak: 14,
  badge: `💡`,
  avatar: `⚔️`
}, {
  rank: 4,
  name: `MATHWIZARD`,
  xp: 9500,
  streak: 10,
  badge: `🎯`,
  avatar: `⚙️`
}, {
  rank: 5,
  name: `CODEMASTER`,
  xp: 8900,
  streak: 8,
  badge: `🏹`,
  avatar: `🏹`
}, {
  rank: 6,
  name: `SCIENCEBOT`,
  xp: 7600,
  streak: 6,
  badge: `⚗`,
  avatar: `🧙`
}, {
  rank: 7,
  name: `HISTORYKING`,
  xp: 6300,
  streak: 5,
  badge: `📜`,
  avatar: `⚔️`
}, {
  rank: 8,
  name: `ARTQUEEN`,
  xp: 5700,
  streak: 4,
  badge: `🎨`,
  avatar: `📚`
}, {
  rank: 9,
  name: `WORDSMITH`,
  xp: 4900,
  streak: 3,
  badge: `✍`,
  avatar: `📚`
}, {
  rank: 10,
  name: `PUZZLEGEEK`,
  xp: 4100,
  streak: 2,
  badge: `🧩`,
  avatar: `⚙️`
}];
export const RANK_STYLES = {
  1: {
    bg: `#ffe94a`,
    glow: `#ffe94a66`,
    icon: `👑`
  },
  2: {
    bg: `#c0c0c0`,
    glow: `#c0c0c066`,
    icon: `🥈`
  },
  3: {
    bg: `#ff8c1a`,
    glow: `#ff8c1a66`,
    icon: `🥉`
  }
};
export const TICKER_ITEMS = [`QUANTUMKID just leveled up! ⭐`, `PRIYA_STAR hit a 18-day streak! 🔥`, `ALEXDOOM earned the PHYSICS MASTER badge! 🏆`, `MATHWIZARD answered 50 questions! 🎯`, `CODEMASTER unlocked CODE WIZARD! 💻`];
export const TOPICS = [`Fractions`, `Probability`, `Algebra`, `Geometry`, `Decimals and Percentages`];
export const masteryColor = e => e >= 70 ? `#4aff91` : e >= 40 ? `#ffe94a` : `#ff3355`;
export const explainConcept = (e, t, n) => t >= 70 ? `${e} is in great shape — ${t}% mastery. Keep it up!` : t >= 40 ? `${e} is developing (${t}%). A bit more practice will get this solid.` : t === 0 && !n ? `No attempts on ${e} yet — nothing to diagnose until you've tried a few questions.` : `${e} is weak (${t}%)${n ? `` : ` — this is likely dragging down the concept above it`}. Worth reviewing directly.`;
