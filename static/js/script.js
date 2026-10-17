document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!expanded));
      sidebar.classList.toggle("mobile-open", !expanded);
    });
  }
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm || "Are you sure?")) event.preventDefault();
    });
  });
  const status = document.getElementById("placement-status");
  const placementFields = document.querySelectorAll(".placement-field");
  function updatePlacementFields() {
    const notPlaced = status && status.value === "Not Placed";
    placementFields.forEach((label) => {
      label.classList.toggle("field-muted", Boolean(notPlaced));
      const input = label.querySelector("input");
      if (input) input.disabled = Boolean(notPlaced);
    });
  }
  if (status) { status.addEventListener("change", updatePlacementFields); updatePlacementFields(); }
});
