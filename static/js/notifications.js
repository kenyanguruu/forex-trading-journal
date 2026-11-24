
document.addEventListener("DOMContentLoaded", function () {

    const notificationContainer = document.getElementById(
        "notification-container"
    );

    const flashContainer = document.getElementById("flash-messages");

    if (!notificationContainer) {
        return;
    }

    // Map Flask message categories to notification types.
    function normalizeType(type) {
        const category = (type || "info").toLowerCase();

        if (["success"].includes(category)) return "success";

        if (["error", "danger"].includes(category)) return "error";

        if (["warning"].includes(category)) return "warning";

        return "info";
    }

    // Display a notification.
    function showNotification(type, message, duration = 5000) {

        if (!message) return;

        const notificationType = normalizeType(type);

        const notification = document.createElement("div");
        notification.className = `notification notification-${notificationType}`;

        notification.setAttribute("role", "status");

        const icons = {
            success: "✓",
            error: "✕",
            warning: "!",
            info: "i"
        };

        const titles = {
            success: "Success",
            error: "Something went wrong",
            warning: "Warning",
            info: "Information"
        };

        const icon = document.createElement("div");
        icon.className = "notification-icon";
        icon.textContent = icons[notificationType];

        const content = document.createElement("div");
        content.className = "notification-content";

        const title = document.createElement("strong");
        title.textContent = titles[notificationType];

        const messageText = document.createElement("p");
        messageText.textContent = message;

        content.appendChild(title);
        content.appendChild(messageText);

        const closeButton = document.createElement("button");
        closeButton.className = "notification-close";
        closeButton.type = "button";
        closeButton.textContent = "×";
        closeButton.setAttribute("aria-label", "Close notification");

        const progress = document.createElement("div");
        progress.className = "notification-progress";

        notification.appendChild(icon);
        notification.appendChild(content);
        notification.appendChild(closeButton);
        notification.appendChild(progress);

        notificationContainer.appendChild(notification);

        // Animate notification entrance.
        requestAnimationFrame(function () {
            notification.classList.add("show");
        });

        let timeout;

        function removeNotification() {
            clearTimeout(timeout);

            notification.classList.remove("show");
            notification.classList.add("hide");

            setTimeout(function () {
                notification.remove();
            }, 300);
        }

        closeButton.addEventListener("click", removeNotification);

        if (duration > 0) {
            progress.style.animationDuration = `${duration}ms`;

            timeout = setTimeout(removeNotification, duration);
        } else {
            progress.style.display = "none";
        }

        // Pause the countdown while the user hovers.
        notification.addEventListener("mouseenter", function () {
            clearTimeout(timeout);
            progress.style.animationPlayState = "paused";
        });

        notification.addEventListener("mouseleave", function () {
            if (duration > 0) {
                progress.style.animationPlayState = "running";
                timeout = setTimeout(removeNotification, 2000);
            }
        });
    }

    // Make notifications available to other JavaScript files.
    window.showNotification = showNotification;

    // Convert Flask flash messages into JavaScript notifications.
    if (flashContainer) {

        const flashMessages = flashContainer.querySelectorAll(
            ".flash-message"
        );

        flashMessages.forEach(function (flashMessage) {

            const type = flashMessage.dataset.category;
            const message = flashMessage.textContent.trim();

            showNotification(type, message);

        });

        flashContainer.remove();
    }

});
