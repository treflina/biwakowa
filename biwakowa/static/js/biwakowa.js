/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./assets/biwakowa.js":
/*!****************************!*\
  !*** ./assets/biwakowa.js ***!
  \****************************/
/***/ (() => {

eval("(() => {\r\n    // navbar\r\n\r\n    let hamburgerBtn = document.querySelector(\".hamburger\");\r\n\r\n    let navMenu = document.querySelector(\".nav-list\");\r\n    let allTargetNavItems = document.querySelectorAll(\".menu-close\");\r\n\r\n    function handleHamburger() {\r\n        if (hamburgerBtn.classList.contains(\"is-active\")) {\r\n            hamburgerBtn.setAttribute(\"aria-expanded\", \"true\");\r\n        } else {\r\n            hamburgerBtn.setAttribute(\"aria-expanded\", \"false\");\r\n        }\r\n    }\r\n\r\n    function toggleHamburger() {\r\n        navMenu.classList.toggle(\"scale-0\");\r\n        navMenu.classList.toggle(\"scale-1\");\r\n        navMenu.classList.toggle(\"opacity-0\");\r\n        navMenu.classList.toggle(\"opacity-1\");\r\n        navMenu.classList.toggle(\"max-h-0\");\r\n        navMenu.classList.toggle(\"max-h-dvh\");\r\n        hamburgerBtn.classList.toggle(\"is-active\");\r\n        hamburgerBtn.classList.toggle(\"absolute\");\r\n        hamburgerBtn.classList.toggle(\"fixed\");\r\n        handleHamburger();\r\n    }\r\n\r\n    const closeNav = () => {\r\n        hamburgerBtn.classList.remove(\"is-active\");\r\n        hamburgerBtn.classList.remove(\"fixed\");\r\n        hamburgerBtn.classList.add(\"absolute\");\r\n        navMenu.classList.remove(\"opacity-1\");\r\n        navMenu.classList.remove(\"scale-1\");\r\n        navMenu.classList.add(\"opacity-0\");\r\n        navMenu.classList.add(\"scale-0\");\r\n        navMenu.classList.remove(\"max-h-dvh\");\r\n        navMenu.classList.add(\"max-h-0\");\r\n        handleHamburger();\r\n    };\r\n\r\n    // toggle hamburger menu\r\n    hamburgerBtn?.addEventListener(\"click\", toggleHamburger);\r\n\r\n    //hide navigation when link clicked\r\n    allTargetNavItems?.forEach((item) => {\r\n        item.addEventListener(\"click\", closeNav);\r\n    });\r\n\r\n    // loading page indicator\r\n    const wait = (delay = 0) =>\r\n        new Promise((resolve) => setTimeout(resolve, delay));\r\n\r\n    const setVisible = (selector, visible) => {\r\n        const el = document.querySelector(selector);\r\n        el !== null && (el.style.display = visible ? \"flex\" : \"none\");\r\n    };\r\n\r\n    setVisible(\".page\", false);\r\n    setVisible(\"#loading\", true);\r\n\r\n    document.addEventListener(\"DOMContentLoaded\", () =>\r\n        wait().then(() => {\r\n            setVisible(\".page\", true);\r\n            setVisible(\"#loading\", false);\r\n        })\r\n    );\r\n})();\r\n\n\n//# sourceURL=webpack://b4b/./assets/biwakowa.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./assets/biwakowa.js"]();
/******/ 	
/******/ })()
;