window.VSLReact = window.VSLReact || {};

window.VSLReact.OPERANT_ACTIONS = [
  "nosepoke_L",
  "nosepoke_R",
  "leverpress",
  "keypeck",
];

window.VSLReact.resolveOperantPair = function resolveOperantPair(first, second) {
  const options = window.VSLReact.OPERANT_ACTIONS || [];
  const fallbackA = options[0] || "nosepoke_L";
  const fallbackB = options[1] || fallbackA;

  const a = options.includes(first) ? first : fallbackA;
  let b = options.includes(second) ? second : fallbackB;
  if (b === a) {
    b = options.find((x) => x !== a) || fallbackB;
  }
  return [a, b];
};
