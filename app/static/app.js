const runButton = document.getElementById("run-button");
const dashboard = document.getElementById("dashboard");
const emptyState = document.getElementById("empty-state");


function formatCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(value);
}


runButton.addEventListener("click", async () => {
    runButton.disabled = true;
    runButton.textContent = "Running recovery...";

    try {
        const response = await fetch("/run-batch?count=80", {
            method: "POST",
        });

        if (!response.ok) {
            throw new Error("Failed to run recovery batch");
        }

        const report = await response.json();

        renderDashboard(report);

        emptyState.classList.add("hidden");
        dashboard.classList.remove("hidden");

    } catch (error) {
        alert(error.message);
    } finally {
        runButton.disabled = false;
        runButton.textContent = "Run Recovery Batch";
    }
});


function renderDashboard(report) {
    document.getElementById("events-processed").textContent =
        report.events_processed;

    document.getElementById("total-at-risk").textContent =
        formatCurrency(report.total_at_risk);

    document.getElementById("total-recovered").textContent =
        formatCurrency(report.total_recovered);

    document.getElementById("recovery-rate").textContent =
        `${report.recovery_rate}%`;


    const oneOff =
        report.by_payment_type.one_off;

    document.getElementById("one-off-rate").textContent =
        `${oneOff.recovery_rate}%`;

    document.getElementById("one-off-details").textContent =
        `${oneOff.events} events · ${formatCurrency(oneOff.recovered)} recovered`;


    const subscription =
        report.by_payment_type.subscription;

    document.getElementById("subscription-rate").textContent =
        `${subscription.recovery_rate}%`;

    document.getElementById("subscription-details").textContent =
        `${subscription.events} events · ${formatCurrency(subscription.recovered)} recovered`;


    document.getElementById("escalation-rate").textContent =
        `${report.escalation_rate}%`;

    document.getElementById("escalation-details").textContent =
        `${report.escalated_count} events escalated`;


    const policyContainer =
        document.getElementById("policy-decisions");

    policyContainer.innerHTML = "";

    for (const [reason, count] of Object.entries(
        report.decision_reason_counts
    )) {
        const item = document.createElement("div");

        item.className = "policy-item";

        item.textContent =
            `${reason.replaceAll("_", " ")}: ${count}`;

        policyContainer.appendChild(item);
    }
}