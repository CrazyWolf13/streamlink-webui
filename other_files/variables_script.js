document.addEventListener("DOMContentLoaded", function () {
    const hostname = "RaspberryPi";
    const title_heading = "Streamlink Web-UI";

    const placeholders = document.querySelectorAll("[data-variable]");

    placeholders.forEach((element) => {
        const variableName = element.dataset.variable;
        switch (variableName) {
            case "hostname":
                element.textContent = hostname;
                break;
            case "title_heading":
                element.textContent = title_heading;
                break;
            default:
                break;
        }
    });
});
