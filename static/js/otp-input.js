document.addEventListener("DOMContentLoaded", function () {

    const otpForms = document.querySelectorAll(".otp-form");

    otpForms.forEach(function (form) {

        const inputs = form.querySelectorAll(".otp-digit");
        const hiddenInput = form.querySelector("#otp");

        function updateOTP() {

            hiddenInput.value = Array.from(inputs)
                .map(input => input.value)
                .join("");

        }

        inputs.forEach(function (input, index) {

            input.addEventListener("input", function () {

                input.value = input.value.replace(/[^0-9]/g, "");

                if (input.value && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }

                updateOTP();

            });

            input.addEventListener("keydown", function (event) {

                if (event.key === "Backspace" && !input.value && index > 0) {

                    inputs[index - 1].focus();

                }

                if (event.key === "ArrowLeft" && index > 0) {
                    inputs[index - 1].focus();
                }

                if (event.key === "ArrowRight" && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }

            });

            input.addEventListener("paste", function (event) {

                event.preventDefault();

                const pastedText = (
                    event.clipboardData || window.clipboardData
                ).getData("text");

                const digits = pastedText.replace(/[^0-9]/g, "").slice(0, 6);

                digits.split("").forEach(function (digit, digitIndex) {

                    inputs[digitIndex].value = digit;

                });

                updateOTP();

                const nextEmpty = Array.from(inputs).find(
                    input => !input.value
                );

                if (nextEmpty) {
                    nextEmpty.focus();
                } else {
                    inputs[inputs.length - 1].focus();
                }

            });

        });

        form.addEventListener("submit", function (event) {

            updateOTP();

            if (hiddenInput.value.length !== 6) {

                event.preventDefault();

                const firstEmpty = Array.from(inputs).find(
                    input => !input.value
                );

                if (firstEmpty) {
                    firstEmpty.focus();
                }

            }

        });

        inputs[0].focus();

    });

});