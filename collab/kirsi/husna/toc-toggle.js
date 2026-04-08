document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("quarto-margin-sidebar");
  const tocNav = document.getElementById("TOC");
  const bootstrapApi = window.bootstrap;

  if (!sidebar || !tocNav || !bootstrapApi || !bootstrapApi.Offcanvas || !bootstrapApi.Modal) {
    return;
  }

  const offcanvas = document.createElement("div");
  offcanvas.className = "offcanvas offcanvas-end report-toc-offcanvas";
  offcanvas.id = "report-toc-offcanvas";
  offcanvas.tabIndex = -1;
  offcanvas.setAttribute("aria-labelledby", "report-toc-title");
  offcanvas.innerHTML = [
    '<div class="offcanvas-header">',
    '<h2 class="offcanvas-title" id="report-toc-title">Contents</h2>',
    '<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>',
    "</div>",
    '<div class="offcanvas-body"></div>'
  ].join("");

  const tocClone = tocNav.cloneNode(true);
  tocClone.id = "report-toc";
  offcanvas.querySelector(".offcanvas-body").appendChild(tocClone);
  document.body.appendChild(offcanvas);

  const offcanvasInstance = new bootstrapApi.Offcanvas(offcanvas);

  const toggleButton = document.createElement("button");
  toggleButton.type = "button";
  toggleButton.className = "toc-toggle-button";
  toggleButton.setAttribute("aria-controls", "report-toc-offcanvas");
  toggleButton.textContent = "TOC";
  toggleButton.addEventListener("click", () => {
    offcanvasInstance.show();
  });
  document.body.appendChild(toggleButton);

  tocClone.addEventListener("click", (event) => {
    const clickedLink = event.target instanceof Element && event.target.closest("a[href^='#']");
    if (!clickedLink) {
      return;
    }
    window.setTimeout(() => offcanvasInstance.hide(), 120);
  });

  const modal = document.createElement("div");
  modal.className = "modal fade figure-zoom-modal";
  modal.id = "figure-zoom-modal";
  modal.tabIndex = -1;
  modal.setAttribute("aria-hidden", "true");
  modal.innerHTML = [
    '<div class="modal-dialog modal-dialog-centered modal-xl">',
    '<div class="modal-content">',
    '<div class="modal-header">',
    '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>',
    "</div>",
    '<div class="modal-body"></div>',
    "</div>",
    "</div>"
  ].join("");
  document.body.appendChild(modal);

  const modalBody = modal.querySelector(".modal-body");
  const modalInstance = new bootstrapApi.Modal(modal);

  const zoomableImages = Array.from(
    document.querySelectorAll(".cell-output-display img, .quarto-figure img")
  ).filter((img) => !img.closest(".dataTables_wrapper"));

  zoomableImages.forEach((img) => {
    img.classList.add("zoomable-figure");
    img.setAttribute("tabindex", "0");
    img.setAttribute("role", "button");

    const openZoom = () => {
      const clone = img.cloneNode(true);
      clone.removeAttribute("width");
      clone.removeAttribute("height");
      modalBody.replaceChildren(clone);
      modalInstance.show();
    };

    img.addEventListener("click", openZoom);
    img.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openZoom();
      }
    });
  });
});
