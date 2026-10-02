console.log("Chess Academy website loaded successfully!");
/* =========================================================
   COURSE CARD FLIP
   ========================================================= */

document.querySelectorAll(".course-card").forEach(function(card) {

    card.addEventListener("click", function() {

        card.classList.toggle("flipped");

    });

});
document.addEventListener("DOMContentLoaded", function () {

    const courseCards = document.querySelectorAll(".course-card");

    courseCards.forEach(function (card) {

        card.addEventListener("click", function () {

            this.classList.toggle("flipped");

        });

    });

});
function togglePassword() {
    const password = document.getElementById("password");
    const button = document.querySelector(".toggle-password");

    if (password.type === "password") {
        password.type = "text";
        button.textContent = "🙈";
    } else {
        password.type = "password";
        button.textContent = "👁️";
    }
}
function toggleSpecificPassword(inputId, button) {

    const password = document.getElementById(inputId);

    if (password.type === "password") {

        password.type = "text";
        button.textContent = "🙈";

    } else {

        password.type = "password";
        button.textContent = "👁️";

    }
}