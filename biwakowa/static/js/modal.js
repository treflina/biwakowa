body = document.querySelector("body");
// const modal = document.getElementsByClassName("modal");
let modal;
const openModal = document.querySelectorAll(".openModal");
const closeModal = document.querySelectorAll(".close");
const modalContent = document.querySelector(".modal__content");

const close = (e) => {
    e.preventDefault();
    modal?.classList.remove("show");
    modal?.classList.add("hide");
    body.style.overflowY = "scroll";
};

openModal.forEach((btn) =>
    btn.addEventListener("click", (e) => {
        e.preventDefault();
        const targetModal = e.currentTarget.getAttribute("data-target");

        modal = document.querySelector(`${targetModal}`);
        modal.classList.add("show");
        modal.classList.remove("hide");
        body.style.overflowY = "hidden";
    })
);

closeModal.forEach((btn) => btn.addEventListener("click", close));

document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        close(e);
    }
});
