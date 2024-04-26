const openMenu = document.querySelector("#open-menu");
const closeMenu = document.querySelector("#close-menu");
const aside = document.querySelector("aside");

openMenu.addEventListener("click", () => {
    aside.classList.add("aside-visible");
})

closeMenu.addEventListener("click", () => {
    aside.classList.remove("aside-visible");
})

/**
 * Alternar la visibilidad del menú desplegable 1.
 * @returns {void}
 */
function toggleDropdown1() {
    document.getElementById("dropdown-content1").classList.toggle("show");
  }

/**
 * Alternar la visibilidad del menú desplegable 2.
 * @returns {void}
 */
function toggleDropdown2() {
    document.getElementById("dropdown-content2").classList.toggle("show");
}

