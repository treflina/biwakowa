const path = require("path");

module.exports = {
    entry: {
        datepicker: "./assets/js/datepicker.js",
        biwakowa: "./assets/js/biwakowa.js",
        modal: "./assets/js/modal.js",
        aos: "./assets/js/aos.js",
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "./biwakowa/static/js"),
    },
};
