const tocRoot = document.querySelector("[data-toc]");
const contentRoot = document.querySelector(".manual-document");

const slugify = (value) =>
  value
    .trim()
    .toLowerCase()
    .replace(/[^\w\u3131-\u318e\uac00-\ud7a3]+/g, "-")
    .replace(/^-+|-+$/g, "") || "section";

const parseHeadingNumbers = (text) => {
  const match = text.match(/^(\d+(?:\.\d+)*)\.?(?:\s+|$)/);
  return match ? match[1].split(".").map(Number) : [];
};

const computeDepths = (items) => {
  const knownPrefixes = new Set(
    items
      .map((item) => item.numbers)
      .filter((numbers) => numbers.length)
      .map((numbers) => numbers.join("."))
  );
  const depthMap = new Map();

  items.forEach((item) => {
    let depth = item.fallbackDepth;
    if (item.numbers.length) {
      let ancestorDepth = 1;
      for (let size = item.numbers.length - 1; size > 0; size -= 1) {
        const prefix = item.numbers.slice(0, size).join(".");
        if (depthMap.has(prefix)) {
          ancestorDepth = depthMap.get(prefix);
          break;
        }
        if (knownPrefixes.has(prefix)) {
          ancestorDepth = size + 1;
          break;
        }
      }
      depth = Math.min(ancestorDepth + 1, 4);
      depthMap.set(item.numbers.join("."), depth);
    }
    item.depth = depth;
  });
};

const buildToc = () => {
  if (!tocRoot || !contentRoot) return [];

  const headingNodes = [
    ...contentRoot.querySelectorAll(".manual-section > h2, .manual-article > h3"),
  ];

  const items = headingNodes
    .map((heading) => {
      const container = heading.parentElement;
      const text = heading.textContent?.trim() || "";
      if (!container || !text) return null;

      if (!container.id) {
        container.id = slugify(text);
      }

      return {
        id: container.id,
        text,
        numbers: parseHeadingNumbers(text),
        fallbackDepth: heading.tagName === "H2" ? 2 : 3,
        depth: heading.tagName === "H2" ? 2 : 3,
      };
    })
    .filter(Boolean);

  computeDepths(items);
  tocRoot.replaceChildren();

  items.forEach((item) => {
    const link = document.createElement("a");
    link.className = `toc-link depth-${item.depth}`;
    link.href = `#${item.id}`;
    link.textContent = item.text;
    tocRoot.append(link);
  });

  return items;
};

const getTocLinks = () => [...document.querySelectorAll("[data-toc] .toc-link")];

const activateCurrentSection = () => {
  const tocLinks = getTocLinks();
  const sections = tocLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

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

buildToc();
window.addEventListener("scroll", activateCurrentSection, { passive: true });
window.addEventListener("load", activateCurrentSection);
