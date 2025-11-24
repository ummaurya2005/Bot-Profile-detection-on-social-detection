document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("bot-form");
    const loading = document.getElementById("loading");
    const btn = document.getElementById("analyze-btn");

    if (!form || !loading || !btn) return;

    // Hide loading initially
    loading.style.display = "none";

    form.addEventListener("submit", (e) => {
        // Prevent double-click submission
        if (btn.disabled) {
            e.preventDefault();
            return;
        }

        // Show loading animation
        loading.style.display = "block";
        loading.style.opacity = "0";
        setTimeout(() => {
            loading.style.opacity = "1";
            loading.style.transition = "opacity 0.25s ease";
        }, 10);

        // Disable button
        btn.disabled = true;
        btn.style.opacity = "0.6";
        btn.style.cursor = "not-allowed";
    });
});
