(() => {
    // navbar

    let hamburgerBtn = document.querySelector(".hamburger");

    let navMenu = document.querySelector(".nav-list");
    let allTargetNavItems = document.querySelectorAll(".menu-close");

    function handleHamburger() {
        if (hamburgerBtn.classList.contains("is-active")) {
            hamburgerBtn.setAttribute("aria-expanded", "true");
        } else {
            hamburgerBtn.setAttribute("aria-expanded", "false");
        }
    }

    function toggleHamburger() {
        navMenu.classList.toggle("scale-0");
        navMenu.classList.toggle("scale-1");
        navMenu.classList.toggle("opacity-0");
        navMenu.classList.toggle("opacity-1");
        navMenu.classList.toggle("max-h-0");
        navMenu.classList.toggle("max-h-dvh");
        hamburgerBtn.classList.toggle("is-active");
        hamburgerBtn.classList.toggle("absolute");
        hamburgerBtn.classList.toggle("fixed");
        handleHamburger();
    }

    const closeNav = () => {
        hamburgerBtn.classList.remove("is-active");
        hamburgerBtn.classList.remove("fixed");
        hamburgerBtn.classList.add("absolute");
        navMenu.classList.remove("opacity-1");
        navMenu.classList.remove("scale-1");
        navMenu.classList.add("opacity-0");
        navMenu.classList.add("scale-0");
        navMenu.classList.remove("max-h-dvh");
        navMenu.classList.add("max-h-0");
        handleHamburger();
    };

    // toggle hamburger menu
    hamburgerBtn?.addEventListener("click", toggleHamburger);

    //hide navigation when link clicked
    allTargetNavItems?.forEach((item) => {
        item.addEventListener("click", closeNav);
    });
})();
