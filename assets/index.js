import Datepicker from "../node_modules/flowbite-datepicker/js/Datepicker";
import DateRangePicker from "../node_modules/flowbite-datepicker/js/DateRangePicker";
import pl from "../node_modules/flowbite-datepicker/js/i18n/locales/pl";

document.addEventListener("DOMContentLoaded", function () {
    Datepicker.locales.pl = pl.pl;

    const today = new Date();

    const datepickerOptions = {
        allowOneSidedRange: true,
        language: "pl",
        weekStart: 1,
        format: "dd.mm.yyyy",
        minDate: today,
        orientation: "bottom",
        todayHighlight: true,
        autohide: true,
        clearButton: true,
    };

    Date.prototype.addDays = function (days) {
        const date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
    };

    const daterangepicker = document.querySelector(".daterangepicker");
    const rangePicker = new DateRangePicker(daterangepicker, datepickerOptions);
    const datepickerStart = document.querySelector(".datepicker1");

    const setEndValue = () => {
        let endValue;
        const startValue = datepickerStart.value;
        const [day, month, year] = [...startValue?.split(".")];
        const monthNum = parseInt(month);
        const startValueDate = new Date(year, monthNum - 1, day);
        if (monthNum === 7 || monthNum === 8) {
            endValue = startValueDate.addDays(7);
        } else {
            endValue = startValueDate.addDays(3);
        }
        rangePicker.setDates(startValue, endValue);
    };

    datepickerStart.addEventListener("changeDate", setEndValue);
    datepickerStart.addEventListener("focus", () => {
        rangePicker.datepickers[1].setDate({ clear: true });
    });
});
