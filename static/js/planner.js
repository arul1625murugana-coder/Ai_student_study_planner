const generateButton =
    document.getElementById("generatePlan");

const message =
    document.getElementById("planMessage");

if (generateButton) {

    generateButton.addEventListener(
        "click",
        async () => {

            generateButton.disabled = true;

            generateButton.innerText =
                "Generating...";

            try {

                const response = await fetch(
                    "/api/planner/generate",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json"
                        }
                    }
                );

                const data =
                    await response.json();

                message.style.display = "block";

                message.className =
                    data.success
                        ? "alert alert-success"
                        : "alert alert-danger";

                message.innerText =
                    data.message;

                if (data.success) {

                    setTimeout(() => {
                        location.reload();
                    }, 1000);

                }

            } catch (error) {

                message.style.display = "block";

                message.className =
                    "alert alert-danger";

                message.innerText =
                    "Something went wrong.";

            }

            generateButton.disabled = false;

            generateButton.innerText =
                "✨ Generate AI Plan";

        }
    );

}