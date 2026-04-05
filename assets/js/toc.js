const tocLinks = [...document.querySelectorAll("[data-toc] .toc-link")];
const sections = tocLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

const activateCurrentSection = () => {
  if (!sections.length) return;
  const fromTop = window.scrollY + 140;
  let current = sections[0];

  for (const section of sections) {
    if (section.offsetTop <= fromTop) {
      current = section;
    }
  }

  tocLinks.forEach((link) => {
    const active = current && link.getAttribute("href") === `#${current.id}`;
    link.classList.toggle("active", active);
  });
};

window.addEventListener("scroll", activateCurrentSection, { passive: true });
window.addEventListener("load", activateCurrentSection);
