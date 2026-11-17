// ?mock=1 runs the game on the UI reference's own fake data (used by the visual comparison
// and for offline demos). Without it, everything comes from the tutor's server.
export const isMock = new URLSearchParams(window.location.search).has('mock');
