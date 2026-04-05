const sidebar = document.querySelector("[data-sidebar]");
const toggleButton = document.querySelector("[data-sidebar-toggle]");

if (sidebar && toggleButton) {
  toggleButton.addEventListener("click", () => {
    const expanded = toggleButton.getAttribute("aria-expanded") === "true";
    toggleButton.setAttribute("aria-expanded", String(!expanded));
    sidebar.classList.toggle("is-open", !expanded);
  });
}
