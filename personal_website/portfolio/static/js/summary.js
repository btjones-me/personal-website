const summaryTabs = document.querySelectorAll("[data-summary-tab]");
const summaryPanels = document.querySelectorAll("[data-summary-panel]");
const cvLink = document.querySelector("[data-cv-link]");
const cvMessage = document.querySelector("[data-summary-message]");

function activateSummaryTab(name) {
  summaryTabs.forEach((tab) => {
    const isActive = tab.dataset.summaryTab === name;
    tab.classList.toggle("is-active", isActive);
    tab.setAttribute("aria-selected", isActive ? "true" : "false");
  });

  summaryPanels.forEach((panel) => {
    const isActive = panel.dataset.summaryPanel === name;
    panel.classList.toggle("is-active", isActive);
    panel.hidden = !isActive;
  });
}

summaryTabs.forEach((tab) => {
  tab.addEventListener("click", () => activateSummaryTab(tab.dataset.summaryTab));
});

if (cvLink && cvMessage) {
  cvLink.addEventListener("click", () => {
    cvMessage.textContent = "CV downloaded.";
  });
}

