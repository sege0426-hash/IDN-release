const sidebar = document.querySelector("[data-sidebar]");
const toggleButton = document.querySelector("[data-sidebar-toggle]");
const searchInput = document.querySelector("[data-search-input]");
const emptyState = document.querySelector("[data-search-empty]");
const getTocLinks = () => [...document.querySelectorAll("[data-toc] .toc-link")];

if (sidebar && toggleButton) {
  toggleButton.addEventListener("click", () => {
    const expanded = toggleButton.getAttribute("aria-expanded") === "true";
    toggleButton.setAttribute("aria-expanded", String(!expanded));
    sidebar.classList.toggle("is-open", !expanded);
  });
}

if (searchInput) {
  const normalize = (value) => value.trim().toLowerCase();

  const filterToc = () => {
    const tocLinks = getTocLinks();
    const keyword = normalize(searchInput.value);
    let visibleCount = 0;

    if (!tocLinks.length) {
      if (emptyState) {
        emptyState.hidden = true;
      }
      return;
    }

    tocLinks.forEach((link) => {
      const matches = !keyword || normalize(link.textContent || "").includes(keyword);
      link.hidden = !matches;
      link.classList.toggle("is-filtered-out", !matches);
      if (matches) {
        visibleCount += 1;
      } else {
        link.classList.remove("active");
      }
    });

    if (emptyState) {
      emptyState.hidden = visibleCount > 0;
    }
  };

  searchInput.addEventListener("input", filterToc);
  filterToc();
}
