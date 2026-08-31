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
        console.error(error);
        alert(error.message);
    } finally {
        runButton.disabled = false;
        runButton.textContent = "Run Recovery Batch";
    }
});

function renderDashboard(report) {
    /*
        Main metrics
    */

    document.getElementById(
        "events-processed"
    ).textContent = report.events_processed;

    document.getElementById(
        "total-at-risk"
    ).textContent = formatCurrency(
        report.total_at_risk
    );

    document.getElementById(
        "total-recovered"
    ).textContent = formatCurrency(
        report.total_recovered
    );

    document.getElementById(
        "recovery-rate"
    ).textContent = `${report.recovery_rate}%`;

    /*
        One-off breakdown
    */

    const oneOff =
        report.by_payment_type.one_off;

    document.getElementById(
        "one-off-rate"
    ).textContent =
        `${oneOff.recovery_rate}%`;

    document.getElementById(
        "one-off-details"
    ).textContent =
        `${oneOff.events} events · ${formatCurrency(
            oneOff.recovered
        )} recovered`;

    /*
        Subscription breakdown
    */

    const subscription =
        report.by_payment_type.subscription;

    document.getElementById(
        "subscription-rate"
    ).textContent =
        `${subscription.recovery_rate}%`;

    document.getElementById(
        "subscription-details"
    ).textContent =
        `${subscription.events} events · ${formatCurrency(
            subscription.recovered
        )} recovered`;

    /*
        Escalation metrics
    */

    document.getElementById(
        "escalation-rate"
    ).textContent =
        `${report.escalation_rate}%`;

    document.getElementById(
        "escalation-details"
    ).textContent =
        `${report.escalated_count} events escalated`;

    /*
        Policy decisions
    */

    renderPolicyDecisions(
        report.decision_reason_counts
    );

    /*
        Event Audit Explorer
    */

    renderEventList(report.events);
}

function renderPolicyDecisions(decisionCounts) {
    const policyContainer =
        document.getElementById(
            "policy-decisions"
        );

    policyContainer.innerHTML = "";

    for (
        const [reason, count]
        of Object.entries(decisionCounts)
    ) {
        const item =
            document.createElement("div");

        item.className = "policy-item";

        const formattedReason =
            reason.replaceAll("_", " ");

        item.textContent =
            `${formattedReason}: ${count}`;

        policyContainer.appendChild(item);
    }
}

function renderEventList(events) {
    const eventList =
        document.getElementById("event-list");

    const eventCount =
        document.getElementById("event-count");

    eventList.innerHTML = "";

    eventCount.textContent = events.length;

    /*
        Reset audit panel whenever
        a new batch is run.
    */

    document
        .getElementById("audit-empty-state")
        .classList.remove("hidden");

    document
        .getElementById("audit-content")
        .classList.add("hidden");

    events.forEach((event) => {
        const item =
            document.createElement("button");

        item.className = "event-item";

        const paymentType =
            event.payment_type.replaceAll(
                "_",
                " "
            );

        const decision =
            event.decision.replaceAll(
                "_",
                " "
            );

        item.innerHTML = `
            <strong>${paymentType}</strong>

            <span>
                ${formatCurrency(event.amount)}
            </span>

            <small>
                ${decision}
            </small>
        `;

        item.addEventListener(
            "click",
            async () => {
                /*
                    Remove active state from
                    previously selected events.
                */

                document
                    .querySelectorAll(".event-item")
                    .forEach((eventItem) => {
                        eventItem.classList.remove(
                            "active"
                        );
                    });

                /*
                    Mark current event as active.
                */

                item.classList.add("active");

                /*
                    Load the event's audit trail.
                */

                await loadAuditTrail(
                    event.event_id
                );
            }
        );

        eventList.appendChild(item);
    });
}

async function loadAuditTrail(eventId) {
    const auditEmptyState =
        document.getElementById(
            "audit-empty-state"
        );

    const auditContent =
        document.getElementById(
            "audit-content"
        );

    try {
        const response = await fetch(
            `/audit-log/${eventId}`
        );

        if (!response.ok) {
            throw new Error(
                "Could not load audit trail"
            );
        }

        const data =
            await response.json();

        /*
            Show audit content.
        */

        auditEmptyState.classList.add(
            "hidden"
        );

        auditContent.classList.remove(
            "hidden"
        );

        /*
            Display event ID.
        */

        document.getElementById(
            "audit-event-id"
        ).textContent = eventId;

        /*
            Render all audit records.
        */

        renderAuditTimeline(
            data.audit_trail
        );
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

function renderAuditTimeline(records) {
    const timeline =
        document.getElementById(
            "audit-timeline"
        );

    timeline.innerHTML = "";

    records.forEach((record) => {
        const item =
            document.createElement("article");

        item.className = "audit-item";

        const details =
            JSON.stringify(
                record.details,
                null,
                2
            );

        const timestamp =
            new Date(
                record.timestamp
            ).toLocaleString(
                "en-IN",
                {
                    dateStyle: "medium",
                    timeStyle: "medium",
                }
            );

        item.innerHTML = `
            <div class="audit-stage">
                ${record.stage}
            </div>

            <div class="audit-time">
                ${timestamp}
            </div>

            <pre>${details}</pre>
        `;

        timeline.appendChild(item);
    });
}