import Swal from "sweetalert2";

(() => {
    const body = document.querySelector("body");
    const modalCustom = document.querySelector("#notificationsModal");
    const openModalBtn = document.querySelector(".openModal");
    const closeModalBtn = document.querySelector(".close");

    const close = (e) => {
        e.preventDefault();
        modalCustom?.classList.remove("show");
        modalCustom?.classList.add("hide");
        modalCustom?.setAttribute("aria-hidden", "true");
        openModalBtn?.focus();
        body.style.overflowY = "scroll";
    };

    const open = (e) => {
        e.preventDefault();
        modalCustom?.classList.add("show");
        modalCustom?.classList.remove("hide");
        modalCustom?.setAttribute("aria-hidden", "false");
        modalCustom?.focus();
        body.style.overflowY = "hidden";
    };

    openModalBtn?.addEventListener("click", open);

    closeModalBtn?.addEventListener("click", close);

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            close(e);
        }
    });

    const Toast = Swal.mixin({
        toast: true,
        timerProgressBar: true,
        timer: 3000,
        position: "bottom-end",
        showConfirmButton: false,
        didOpen: (toast) => {
            toast.onmouseenter = Swal.stopTimer;
            toast.onmouseleave = Swal.resumeTimer;
        },
    });

    // htmx.logAll();

    document.addEventListener("htmx:beforeSwap", (e) => {
        if (e.detail.xhr.response.includes('id="403"')) {
            e.stopPropagation();
            document.children[0].innerHTML = e.detail.xhr.response;
        }
    });

    document.addEventListener("htmx:confirm", function (evt) {
        if (
            !evt.detail.elt.hasAttribute("confirm-swal") &&
            !evt.detail.elt.hasAttribute("confirm-swal2")
        ) {
            return;
        }

        const question =
            evt.detail.elt.getAttribute("confirm-swal") ||
            evt.detail.elt.getAttribute("confirm-swal2");
        const swalTile = evt.detail.elt.getAttribute("title-swal");
        const swalExpl = evt.detail.elt.getAttribute("expl-swal");

        const nextElementToFocus =
            evt.detail.elt
                .closest("tr")
                ?.nextElementSibling?.querySelector("a") ??
            evt.detail.elt
                .closest("tr")
                ?.previousElementSibling?.querySelector("button") ??
            document.querySelector(".pagination")?.querySelector("button");

        evt.preventDefault();

        const iconSvg = `<svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"></path>
                            </svg>`;

        const questionSvg = `<svg class="h-6 w-6 text-green-800" fill="green" stroke-width="1.5" stroke="currentColor" aria-hidden="true" viewBox="0 0 288 448">
                                    <path d="M 64 128 Q 65 101 83 83 L 83 83 L 83 83 Q 101 65 128 64 L 160 64 L 160 64 Q 187 65 205 83 Q 223 101 224 128 L 224 132 L 224 132 Q 223 166 195 185 L 152 213 L 152 213 Q 113 239 112 287 L 112 288 L 112 288 Q 112 302 121 311 Q 130 320 144 320 Q 158 320 167 311 Q 176 302 176 288 L 176 287 L 176 287 Q 176 274 187 266 L 229 239 L 229 239 Q 257 221 272 193 Q 288 165 288 131 L 288 128 L 288 128 Q 287 74 251 37 Q 214 1 160 0 L 128 0 L 128 0 Q 74 1 37 37 Q 1 74 0 128 Q 0 142 9 151 Q 18 160 32 160 Q 46 160 55 151 Q 64 142 64 128 L 64 128 Z M 144 448 Q 167 447 179 428 Q 189 408 179 388 Q 167 369 144 368 Q 121 369 109 388 Q 99 408 109 428 Q 121 447 144 448 L 144 448 Z" />
                                </svg>`;

        const text =
            question.includes("zatwierdzić") || question.includes("wysłać")
                ? "Czy na pewno"
                : "Czy na pewno usunąć";
        Swal.fire({
            title: swalTile || "Ostrzeżenie",
            html: [`${text} ${question}?`, `${swalExpl || ""}`].join(
                "<br class='mb-2'>"
            ),
            showCancelButton: true,
            cancelButtonText: "Wróć",
            confirmButtonText: "Tak",
            buttonsStyling: false,
            icon: "warning",
            iconHtml: swalTile ? questionSvg : iconSvg,
            position: "top",
            customClass: {
                popup: "swal2-popup1",
                icon: "swal2-icon1",
                title: "swal2-title1",
                htmlContainer: "swal2-html-container1",
                actions: "swal2-actions1",
                confirmButton: "swal2-confirm1",
                cancelButton: "swal2-cancel1",
            },
        }).then((result) => {
            if (result.isConfirmed) {
                nextElementToFocus?.focus();
                evt.detail.issueRequest(true);
            }
        });
    });

    document.addEventListener("showToast", function (evt) {
        const { msg, err } = evt.detail || {};
        const isError = Boolean(err);

        Toast.fire({
            background: isError ? "rgb(254 226 226)" : "#e0f6e2",
            text: msg || err || "Data has been successfully changed.",
        });
    });
})();

// document.addEventListener("DOMContentLoaded", () => {
//     const notificationBtn = document.querySelector("#openNotifications");
//     const handleNotifications = () => {
//         Swal.fire({
//             title: "Ustawienia powiadomień",
//             html: `
//             <div class="my-4">
//                 <!-- Django WebPush button rendered via template tag -->
//                 ${document.getElementById("webpushButtonTemplate").innerHTML}
//             </div>
//         `,
//             showCloseButton: true,
//             showConfirmButton: false,
//             customClass: {
//                 popup: "p-4 rounded shadow-lg",
//                 title: "text-lg font-semibold",
//             },
//         });
//     };
//     notificationBtn?.addEventListener("click", handleNotifications);
// });
