const tooltipTriggerList = document.querySelectorAll("[data-bs-toggle=\"tooltip\"]")
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-masonry-preview]").forEach(preview => {
    const grid = preview.querySelector("[data-masonry]")
    const button = preview.querySelector(".masonry-preview-expand")
    let expanded = false

    function updatePreview() {
      if (expanded) return
      preview.classList.add("is-clipped")
      const overflowing = preview.scrollHeight > preview.clientHeight + 1
      preview.classList.toggle("is-clipped", overflowing)
      button.hidden = !overflowing
    }

    function expand() {
      expanded = true
      preview.classList.remove("is-clipped")
      button.setAttribute("aria-expanded", "true")
      button.hidden = true
    }

    button.addEventListener("click", () => {
      expand()
      grid.focus({preventScroll: true})
    })

    // Reveal clipped content when reached with a keyboard.
    grid.addEventListener("focusin", event => {
      if (!expanded && event.target.getBoundingClientRect().bottom >
        preview.getBoundingClientRect().bottom - button.offsetHeight) {
        expand()
      }
    })

    // Masonry, responsive columns, and images can all change the grid height.
    const observer = new ResizeObserver(updatePreview)
    observer.observe(grid)
    updatePreview()
  })

  function layoutGrid(grid) {
    if (!window.Masonry || !grid.offsetWidth) return

    const masonry = Masonry.data(grid)
    if (masonry) {
      masonry.layout()
    } else {
      new Masonry(grid, JSON.parse(grid.getAttribute("data-masonry")))
    }
  }

  function layoutCollapse(event) {
    // Update both grids revealed by a collapse and grids containing card details.
    event.target.querySelectorAll("[data-masonry]").forEach(layoutGrid)
    const parentGrid = event.target.closest("[data-masonry]")
    if (parentGrid) layoutGrid(parentGrid)
  }

  document.addEventListener("shown.bs.collapse", layoutCollapse)
  document.addEventListener("hidden.bs.collapse", layoutCollapse)

  // Images can change card heights after the initial layout.
  document.addEventListener("load", event => {
    if (event.target.tagName !== "IMG") return
    const grid = event.target.closest("[data-masonry]")
    if (grid) layoutGrid(grid)
  }, true)
  window.addEventListener("load", () => {
    document.querySelectorAll("[data-masonry]").forEach(layoutGrid)
  })

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

  ;(function () {
    // Contact form
    const form = document.querySelector("#contact-form")
    const statusDiv = document.getElementById("form-status")
    if (!form || !statusDiv) return

    form.addEventListener("submit", async (event) => {
      event.preventDefault()
      event.stopPropagation()

      form.classList.add("was-validated")

      if (!form.checkValidity()) {
        return
      }

      const name = form.name.value.trim()
      const email = form.email.value.trim()
      const message = form.message.value.trim()

      try {
        const response = await fetch(form.dataset.endpoint, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({name, email, message})
        })

        const result = await response.json()

        if (response.ok) {
          statusDiv.className = "alert alert-success"
          statusDiv.textContent = result.message || form.dataset.messageSent
          form.reset()
          form.classList.remove("was-validated")
        } else {
          statusDiv.className = "alert alert-danger"
          statusDiv.textContent = result.message || form.dataset.messageFailed
        }
      } catch (err) {
        statusDiv.className = "alert alert-danger"
        statusDiv.textContent = form.dataset.messageUnknown
      }

      statusDiv.classList.remove("d-none")
    })
  })()
})