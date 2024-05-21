// navbar

const hamburgerBtn = document.querySelector(".hamburger");

const navMenu = document.querySelector(".nav-list");
const allTargetNavItems = document.querySelectorAll(".menu-close");

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
hamburgerBtn.addEventListener("click", toggleHamburger);

//hide navigation when link clicked
allTargetNavItems.forEach((item) => {
    item.addEventListener("click", closeNav);
});

const calendars = document.querySelectorAll(".calendar-days");
const firstDayData = document.getElementById("firstDay")?.textContent;
const firstDayNum = firstDayData && JSON.parse(firstDayData);

calendars?.forEach((cal) => {
    let firstLiTag = cal.querySelector("li");
    firstLiTag.style.gridColumnStart = firstDayNum + 1;
});

// document.addEventListener("DOMContentLoaded", function (event) {
//     const calendarsSection = document.getElementById("calendars");
//     const btnLinks = document.getElementsByClassName("cal-link");

//     const d = new Date();
//     let month = d.getMonth();
//     let year = d.getFullYear();

//     // const removeAndSetActiveClass = (p) => {
//     //     [...btnLinks].forEach((btn) => {
//     //         btn.classList.remove("active");
//     //         if (btn.classList.contains(`pagination-link-${p}`)) {
//     //             btn.classList.add("active");
//     //         }
//     //     });
//     // };

//     const getCalendars = (month, year) => {
//         const newDiv = document.createElement("div");
//         newDiv.classList.add("loader");
//         calendarsSection.appendChild(newDiv);

//         fetch(`/apartament-typu-midi/calendar/${year}/${month}/`, {
//             method: "GET",
//             headers: {
//                 "X-Requested-With": "XMLHttpRequest",
//             },
//         })
//             .then(function (response) {
//                 console.log("hmm");
//                 return response.text();
//             })
//             .then(function (data) {
//                 while (calendarsSection.firstChild) {
//                     calendarsSection.removeChild(calendarsSection.firstChild);
//                 }
//                 calendarsSection.insertAdjacentHTML("afterbegin", data);
//             })
//             .catch(function (err) {
//                 console.warn("Something went wrong.", err);
//             });
//     };

//     getCalendars(month, year);

//     [...btnLinks].forEach((btn) => {
//         btn.addEventListener("click", function getCalendarsAfterClick(e) {
//             e.preventDefault();

//             month = btn.getAttribute("href").split("/").at(-2);
//             year = btn.getAttribute("href").split("/").at(-3);
//             console.log(month, year);
//             if (!month || !year) {
//                 const d = new Date();
//                 month = d.getMonth();
//                 year = d.getFullYear();
//             }

//             getCalendars(month, year);

//             // removeAndSetActiveClass(page);
//             document
//                 .getElementById("calendars")
//                 .scrollIntoView({ behavior: "smooth" });
//         });
//     });
// });
