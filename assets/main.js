// Greenbody – kleine Helfer, ohne Abhaengigkeiten
document.addEventListener("DOMContentLoaded", () => {
  // Mobile Navigation
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("nav");
  toggle?.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!open));
    nav.classList.toggle("is-open", !open);
  });

  // YouTube erst nach Klick laden (Datenschutz)
  document.querySelectorAll(".yt").forEach((box) => {
    box.querySelector(".yt__btn")?.addEventListener("click", () => {
      const iframe = document.createElement("iframe");
      iframe.src = `https://www.youtube-nocookie.com/embed/${box.dataset.id}?autoplay=1`;
      iframe.title = "YouTube-Video";
      iframe.allow = "accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      box.replaceChildren(iframe);
      box.classList.add("is-playing");
    });
  });

  // Themenfilter auf /blog/
  const filters = document.querySelectorAll(".filters button");
  filters.forEach((btn) => {
    btn.addEventListener("click", () => {
      filters.forEach((b) => b.classList.toggle("is-active", b === btn));
      document.querySelectorAll("#list .card").forEach((card) => {
        card.hidden = Boolean(btn.dataset.filter) && card.dataset.topic !== btn.dataset.filter;
      });
    });
  });
});
