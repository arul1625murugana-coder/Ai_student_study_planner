document.addEventListener("DOMContentLoaded", () => {

    const alerts = document.querySelectorAll(".alert");

    setTimeout(() => {

        alerts.forEach(alert => {

            alert.style.transition = "opacity 0.5s";

            alert.style.opacity = "0";

        });

    }, 4000);

});