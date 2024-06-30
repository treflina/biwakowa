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

/***/ "./assets/modal.js":
/*!*************************!*\
  !*** ./assets/modal.js ***!
  \*************************/
/***/ (() => {

eval("const body = document.querySelector(\"body\");\r\n\r\nlet modal;\r\nconst openModal = document.querySelectorAll(\".openModal\");\r\nconst closeModal = document.querySelectorAll(\".close\");\r\nconst modalContent = document.querySelector(\".modal__content\");\r\n\r\nconst close = (e) => {\r\n    e.preventDefault();\r\n    modal?.classList.remove(\"show\");\r\n    modal?.classList.add(\"hide\");\r\n    body.style.overflowY = \"scroll\";\r\n};\r\n\r\nopenModal.forEach((btn) =>\r\n    btn.addEventListener(\"click\", (e) => {\r\n        e.preventDefault();\r\n        const targetModal = e.currentTarget.getAttribute(\"data-target\");\r\n\r\n        modal = document.querySelector(`${targetModal}`);\r\n        modal.classList.add(\"show\");\r\n        modal.classList.remove(\"hide\");\r\n        body.style.overflowY = \"hidden\";\r\n    })\r\n);\r\n\r\ncloseModal.forEach((btn) => btn.addEventListener(\"click\", close));\r\n\r\ndocument.addEventListener(\"keydown\", (e) => {\r\n    if (e.key === \"Escape\") {\r\n        close(e);\r\n    }\r\n});\r\n\n\n//# sourceURL=webpack://b4b/./assets/modal.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./assets/modal.js"]();
/******/ 	
/******/ })()
;