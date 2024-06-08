module.exports = {
    theme: {
        extend: {
            maxWidth: {
                wrapper: "1300px",
            },
        },
        screens: {
            xsm: "400px",
            sm: "640px",
            // => @media (min-width: 640px) { ... }

            md: "768px",
            mdl: "870px",
            // => @media (min-width: 768px) { ... }

            lg: "1024px",
            // => @media (min-width: 1024px) { ... }

            xl: "1280px",
            // => @media (min-width: 1280px) { ... }

            "2xl": "1536px",
            // => @media (min-width: 1536px) { ... }
        },
    },
};
