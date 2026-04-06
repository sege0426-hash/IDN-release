const screenshotSelector = ".manual-screenshot";
const screenshots = [...document.querySelectorAll(screenshotSelector)];

if (screenshots.length) {
  const lightbox = document.createElement("div");
  lightbox.className = "screenshot-lightbox";
  lightbox.hidden = true;
  lightbox.setAttribute("aria-hidden", "true");

  lightbox.innerHTML = `
    <div class="screenshot-lightbox-backdrop" data-lightbox-close></div>
    <div class="screenshot-lightbox-panel" role="dialog" aria-modal="true" aria-label="스크린샷 전체 화면 보기">
      <button class="screenshot-lightbox-close" type="button" aria-label="전체 화면 닫기" data-lightbox-close>&times;</button>
      <figure class="screenshot-lightbox-figure">
        <img class="screenshot-lightbox-image" alt="" />
        <figcaption class="screenshot-lightbox-caption"></figcaption>
      </figure>
    </div>
  `;

  document.body.append(lightbox);

  const lightboxImage = lightbox.querySelector(".screenshot-lightbox-image");
  const lightboxCaption = lightbox.querySelector(".screenshot-lightbox-caption");
  let lastFocusedElement = null;

  const closeLightbox = () => {
    lightbox.hidden = true;
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.removeProperty("overflow");
    if (lastFocusedElement instanceof HTMLElement) {
      lastFocusedElement.focus();
    }
  };

  const openLightbox = (image) => {
    const caption =
      image.closest(".screenshot-card")?.querySelector(".screenshot-caption")?.textContent?.trim() ||
      image.alt ||
      "스크린샷";

    lightboxImage.src = image.currentSrc || image.src;
    lightboxImage.alt = image.alt || caption;
    lightboxCaption.textContent = caption;
    lastFocusedElement = image;
    lightbox.hidden = false;
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    lightbox.querySelector(".screenshot-lightbox-close")?.focus();
  };

  screenshots.forEach((image) => {
    image.tabIndex = 0;
    image.setAttribute("role", "button");
    image.setAttribute("aria-label", `${image.alt || "스크린샷"} 전체 화면으로 보기`);

    image.addEventListener("click", () => openLightbox(image));
    image.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openLightbox(image);
      }
    });
  });

  lightbox.addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof HTMLElement && target.hasAttribute("data-lightbox-close")) {
      closeLightbox();
    }
  });

  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !lightbox.hidden) {
      closeLightbox();
    }
  });
}
