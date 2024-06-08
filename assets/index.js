import Datepicker from "./../node_modules/flowbite-datepicker/js/Datepicker";
import pl from "./../node_modules/flowbite-datepicker/js/i18n/locales/pl";

document.addEventListener("DOMContentLoaded", function () {
    Datepicker.locales.pl = pl.pl;

    const today = new Date();

    const datepickerOptions = {
        language: "pl",
        weekStart: 1,
        format: "dd.mm.yyyy",
        minDate: today,
        orientation: "bottom",
        todayHighlight: true,
        autohide: true,
    };

    document.querySelectorAll(".datepicker").forEach((dp) => {
        new Datepicker(dp, datepickerOptions);
    });
});
