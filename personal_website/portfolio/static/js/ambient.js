const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const orbs = document.querySelectorAll("[data-orb]");
let rafId = null;
let pointer = { x: 0.5, y: 0.5 };

function applyParallax() {
  const intensity = 18;
  const xOffset = (pointer.x - 0.5) * intensity;
  const yOffset = (pointer.y - 0.5) * intensity * 0.7;

  orbs.forEach((orb, index) => {
    const depth = 1 + index * 0.25;
    const tx = xOffset / depth;
    const ty = yOffset / depth;
    orb.style.setProperty("--parallax-x", `${tx}px`);
    orb.style.setProperty("--parallax-y", `${ty}px`);
  });

  rafId = null;
}

function scheduleParallax() {
  if (rafId) {
    return;
  }
  rafId = requestAnimationFrame(applyParallax);
}

function handlePointerMove(event) {
  pointer = {
    x: event.clientX / window.innerWidth,
    y: event.clientY / window.innerHeight,
  };
  scheduleParallax();
}

if (!prefersReducedMotion && orbs.length > 0) {
  window.addEventListener("pointermove", handlePointerMove);
  applyParallax();
}

