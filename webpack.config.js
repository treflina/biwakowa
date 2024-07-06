const path = require("path");

module.exports = {
    entry: {
        datepicker: "./assets/datepicker.js",
        biwakowa: "./assets/biwakowa.js",
        modal: "./assets/modal.js",
        aos: "./assets/aos.js",
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "./biwakowa/static/js"),
    },
};
