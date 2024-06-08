const path = require("path");

module.exports = {
    entry: "./assets/index.js", // path to our input file
    output: {
        filename: "main.js", // output bundle file name
        path: path.resolve(__dirname, "./biwakowa/static/js"), // path to our Django static directory
    },
};
