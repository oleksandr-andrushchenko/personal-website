const tooltipTriggerList = document.querySelectorAll("[data-bs-toggle=\"tooltip\"]")
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".btn-toggle").forEach(btn => {
    const icon = btn.querySelector("i")
    const targetSelector = btn.getAttribute("data-bs-target")
    const target = document.querySelector(targetSelector)

    if (!target) return

    target.addEventListener("show.bs.collapse", () => {
      icon.classList.remove("bi-chevron-down")
      icon.classList.add("bi-chevron-up")
    })

    target.addEventListener("hide.bs.collapse", () => {
      icon.classList.remove("bi-chevron-up")
      icon.classList.add("bi-chevron-down")
    })
  })
})