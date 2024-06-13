const path = require("path");

module.exports = {
    mode: "production",
    entry: {
        datepicker: "./assets/datepicker.js",
        biwakowa: "./assets/biwakowa.js",
        modal: "./assets/biwakowa.js",
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "./biwakowa/static/js"),
    },
};
