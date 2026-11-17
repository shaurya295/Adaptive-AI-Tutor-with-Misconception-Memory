// Every screen the app can show, in the order the reference defines them.
export const SCREENS = [
  'landing', 'signin', 'mainmenu', 'welcome', 'avatarselect', 'howitworks', 'pretest', 'lesson', 'posttest',
  'progress', 'sessioncomplete', 'reward', 'freequest', 'leaderboard', 'evalmetrics', 'misconceptions',
  'spacedrepeat', 'switchstudent',
];

// ?screen=<name> opens that screen directly. Used by the visual comparison and handy while
// building; ignored unless the name is a real screen.
export function initialScreen(fallback) {
  const wanted = new URLSearchParams(window.location.search).get('screen');
  return SCREENS.includes(wanted) ? wanted : fallback;
}
