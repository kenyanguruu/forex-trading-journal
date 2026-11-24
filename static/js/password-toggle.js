
document.addEventListener("DOMContentLoaded", function () {

    const toggleButtons = document.querySelectorAll(".password-toggle");

    toggleButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const input = document.getElementById(button.dataset.target);

            if (!input) return;

            const isPassword = input.type === "password";

            input.type = isPassword ? "text" : "password";

            button.classList.toggle("active", isPassword);

            button.setAttribute(
                "aria-label",
                isPassword ? "Hide password" : "Show password"
            );

            button.setAttribute(
                "title",
                isPassword ? "Hide password" : "Show password"
            );

        });

    });

});
