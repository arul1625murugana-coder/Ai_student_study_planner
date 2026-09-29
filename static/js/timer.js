let totalSeconds = 25 * 60;
let timer = null;

function updateTimer() {

    const minutes =
        Math.floor(totalSeconds / 60);

    const seconds =
        totalSeconds % 60;

    const display =
        document.getElementById("timer");

    if (display) {

        display.innerText =
            `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    }
}

function startTimer() {

    if (timer) return;

    timer = setInterval(() => {

        if (totalSeconds <= 0) {

            clearInterval(timer);

            timer = null;

            alert("Focus session completed! 🎉");

            return;
        }

        totalSeconds--;

        updateTimer();

    }, 1000);
}

function pauseTimer() {

    clearInterval(timer);

    timer = null;
}

function resetTimer() {

    pauseTimer();

    totalSeconds = 25 * 60;

    updateTimer();
}

updateTimer();