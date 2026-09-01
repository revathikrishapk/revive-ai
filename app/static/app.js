/* =========================================================
   REVIVE — FRONTEND APPLICATION
   Connected to the actual FastAPI backend
   ========================================================= */
console.log("REVIVE NEW APP.JS LOADED");
const API_BASE = "";


/* =========================================================
   DOM HELPERS
   ========================================================= */

function $(id) {
    return document.getElementById(id);
}


/* =========================================================
   FORMATTING
   ========================================================= */

function formatCurrency(value) {
    const amount = Number(value || 0);

    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(amount);
}


function formatPercent(value) {
    return `${Number(value || 0).toFixed(2)}%`;
}


function formatName(value) {
    if (!value) {
        return "Unknown";
    }

    return String(value)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}


/* =========================================================
   TOAST
   ========================================================= */

function showToast(message) {
    const toast = $("toast");
    const toastMessage = $("toastMessage");

    if (!toast || !toastMessage) {
        return;
    }

    toastMessage.textContent = message;

    toast.classList.add("visible");

    setTimeout(() => {
        toast.classList.remove("visible");
    }, 3000);
}


/* =========================================================
   API — RUN BATCH
   ========================================================= */

async function runRecoveryBatch() {

    /*
       Your FastAPI endpoint is:

       POST /run-batch?count=80

       It returns the report directly.
    */

    const response = await fetch(
        `${API_BASE}/run-batch?count=80`,
        {
            method: "POST"
        }
    );

    if (!response.ok) {

        let message =
            `Request failed (${response.status})`;

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch (_) {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    return await response.json();
}


/* =========================================================
   API — AUDIT LOG
   ========================================================= */

async function getAuditLog(eventId) {

    const response = await fetch(
        `${API_BASE}/audit-log/${encodeURIComponent(eventId)}`
    );

    if (!response.ok) {

        let message =
            `Audit request failed (${response.status})`;

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch (_) {
            // Keep default message.
        }

        throw new Error(message);
    }

    return await response.json();
}


/* =========================================================
   BUTTON LOADING STATE
   ========================================================= */

function setLoading(isLoading) {

    const buttons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn")
    ];

    buttons.forEach(button => {

        if (!button) {
            return;
        }

        if (isLoading) {

            if (!button.dataset.originalText) {
                button.dataset.originalText =
                    button.innerHTML;
            }

            button.disabled = true;
            button.classList.add("loading");

            button.innerHTML =
                "Running recovery...";

        } else {

            button.disabled = false;
            button.classList.remove("loading");

            if (button.dataset.originalText) {

                button.innerHTML =
                    button.dataset.originalText;

                delete button.dataset.originalText;
            }
        }
    });
}


/* =========================================================
   KPI METRICS
   ========================================================= */

function updateMetrics(report) {

    $("atRiskMetric").textContent =
        formatCurrency(
            report.total_at_risk
        );

    $("recoveredMetric").textContent =
        formatCurrency(
            report.total_recovered
        );

    $("recoveryRateMetric").textContent =
        formatPercent(
            report.recovery_rate
        );

    $("escalationRateMetric").textContent =
        formatPercent(
            report.escalation_rate
        );
}


/* =========================================================
   PAYMENT TYPE PERFORMANCE
   ========================================================= */

function updatePaymentTypePerformance(report) {

    const stats =
        report.by_payment_type || {};

    const oneOff =
        stats.one_off || {};

    const subscription =
        stats.subscription || {};


    const oneOffRate =
        Number(
            oneOff.recovery_rate || 0
        );

    const subscriptionRate =
        Number(
            subscription.recovery_rate || 0
        );


    $("oneOffEvents").textContent =
        `${oneOff.events || 0} events`;

    $("subscriptionEvents").textContent =
        `${subscription.events || 0} events`;


    $("oneOffRate").textContent =
        formatPercent(
            oneOffRate
        );

    $("subscriptionRate").textContent =
        formatPercent(
            subscriptionRate
        );


    $("oneOffBar").style.width =
        `${Math.min(oneOffRate, 100)}%`;

    $("subscriptionBar").style.width =
        `${Math.min(subscriptionRate, 100)}%`;
}


/* =========================================================
   FAILURE CATEGORIES
   ========================================================= */

function updateCategoryList(report) {

    const container =
        $("categoryList");

    const categories =
        report.by_failure_category || {};

    const entries =
        Object.entries(categories);


    if (entries.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No category data available.
            </div>
        `;

        return;
    }


    /*
       Most frequent failure categories first.
    */

    entries.sort(
        ([, a], [, b]) =>
            Number(b.events || 0)
            -
            Number(a.events || 0)
    );


    container.innerHTML =
        entries
            .map(([category, stats]) => {

                return `
                    <div class="category-item">

                        <div>

                            <div class="category-name">
                                ${formatName(category)}
                            </div>

                            <div class="category-meta">
                                ${stats.events || 0} events
                                ·
                                ${formatCurrency(
                                    stats.recovered || 0
                                )}
                                recovered
                            </div>

                        </div>

                        <div class="category-rate">
                            ${formatPercent(
                                stats.recovery_rate
                            )}
                        </div>

                    </div>
                `;

            })
            .join("");
}


/* =========================================================
   EVENT STATUS
   ========================================================= */

function getEventStatus(event) {

    const recoveryStatus =
        event.recovery_status || "";

    const decision =
        event.decision || "";

    const status =
        event.status || "";


    if (
        recoveryStatus === "recovered"
        ||
        Number(event.recovered_amount || 0) > 0
    ) {

        return {
            label: "Recovered",
            className: "recovered"
        };
    }


    if (
        recoveryStatus === "failed"
    ) {

        return {
            label: "Recovery failed",
            className: "failed"
        };
    }


    if (
        decision === "escalate_to_human"
        ||
        decision === "ESCALATE_TO_HUMAN"
    ) {

        return {
            label: "Escalated",
            className: "escalated"
        };
    }


    if (
        status === "duplicate_skipped"
    ) {

        return {
            label: "Duplicate skipped",
            className: ""
        };
    }


    return {
        label: "Not attempted",
        className: ""
    };
}


/* =========================================================
   EVENT LIST
   ========================================================= */

function updateEventList(report) {

    const container =
        $("eventList");

    const events =
        report.events || [];


    $("activityCount").textContent =
        events.length;


    if (events.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No events available.
            </div>
        `;

        return;
    }


    /*
       Display the first 50 events.

       The report may contain all 80 events,
       but keeping the visible list smaller
       keeps the UI clean.
    */

    const visibleEvents =
        events.slice(0, 50);


    container.innerHTML =
        visibleEvents
            .map((event, index) => {

                const status =
                    getEventStatus(event);


                return `
                    <div
                        class="event-item"
                        data-event-index="${index}"
                    >

                        <div class="event-main">

                            <strong>
                                ${formatName(
                                    event.diagnosis
                                    || "unknown"
                                )}
                            </strong>

                            <span>
                                ${formatName(
                                    event.payment_type
                                    || "unknown"
                                )}
                                ·
                                ${escapeHtml(
                                    event.event_id
                                )}
                            </span>

                            <span
                                class="
                                    event-status
                                    ${status.className}
                                "
                            >
                                ${status.label}
                            </span>

                        </div>


                        <div class="event-amount">

                            ${formatCurrency(
                                event.amount
                            )}

                        </div>

                    </div>
                `;

            })
            .join("");


    /*
       Attach event listeners.
    */

    container
        .querySelectorAll(".event-item")
        .forEach(item => {

            item.addEventListener(
                "click",
                async () => {

                    const index =
                        Number(
                            item.dataset.eventIndex
                        );

                    await selectEvent(
                        visibleEvents[index],
                        item
                    );
                }
            );
        });
}


/* =========================================================
   EVENT SELECTION
   ========================================================= */

async function selectEvent(
    event,
    element
) {

    document
        .querySelectorAll(".event-item")
        .forEach(item => {

            item.classList.remove(
                "selected"
            );
        });


    element.classList.add(
        "selected"
    );


    renderAuditLoading(
        event
    );


    try {

        const audit =
            await getAuditLog(
                event.event_id
            );

        renderAuditTrace(
            audit,
            event
        );

    } catch (error) {

        console.error(
            "Audit error:",
            error
        );

        renderAuditError(
            error.message
        );
    }
}


/* =========================================================
   AUDIT LOADING
   ========================================================= */

function renderAuditLoading(event) {

    const panel =
        $("auditPanel");

    panel.innerHTML = `
        <div class="audit-header">

            <h3>
                ${formatCurrency(
                    event.amount
                )}
                payment
            </h3>

            <p>
                ${escapeHtml(
                    event.event_id
                )}
                ·
                ${formatName(
                    event.payment_type
                )}
            </p>

        </div>

        <div
            id="auditTrace"
            class="audit-trace"
        >

            <div class="empty-state">
                Loading recovery trace...
            </div>

        </div>
    `;
}


/* =========================================================
   AUDIT TRACE
   ========================================================= */

function renderAuditTrace(
    audit,
    event
) {

    const container =
        $("auditTrace");


    /*
       Your backend returns:

       {
           "event_id": "...",
           "audit_trail": [...]
       }

       So this is the important correction.
    */

    const entries =
        audit.audit_trail || [];


    if (entries.length === 0) {

        container.innerHTML = `
            <div class="empty-state">
                No audit entries available.
            </div>
        `;

        return;
    }


    container.innerHTML =
        entries
            .map(entry => {

                const stage =
                    entry.stage
                    ||
                    entry.state
                    ||
                    entry.event
                    ||
                    entry.action
                    ||
                    "EVENT";


                const detail =
                    entry.detail
                    ||
                    entry.message
                    ||
                    entry.reason
                    ||
                    "";


                let metadata = "";


                /*
                   Show additional audit metadata
                   when available.
                */

                const data =
                    entry.data
                    ||
                    entry.metadata
                    ||
                    null;


                if (
                    data
                    &&
                    typeof data === "object"
                ) {

                    metadata = `
                        <pre>${escapeHtml(
                            JSON.stringify(
                                data,
                                null,
                                2
                            )
                        )}</pre>
                    `;
                }


                return `
                    <div class="audit-step">

                        <div class="audit-dot"></div>

                        <div>

                            <strong>
                                ${formatName(
                                    String(stage)
                                )}
                            </strong>

                            ${
                                detail
                                    ? `
                                        <span>
                                            ${escapeHtml(
                                                String(detail)
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                            ${metadata}

                        </div>

                    </div>
                `;

            })
            .join("");
}


/* =========================================================
   AUDIT ERROR
   ========================================================= */

function renderAuditError(
    message
) {

    const container =
        $("auditTrace");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="empty-state">

            Unable to load audit trace.

            <br><br>

            ${escapeHtml(message)}

        </div>
    `;
}


/* =========================================================
   HTML ESCAPING
   ========================================================= */

function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   UPDATE DASHBOARD
   ========================================================= */

function updateDashboard(report) {

    updateMetrics(
        report
    );

    updatePaymentTypePerformance(
        report
    );

    updateCategoryList(
        report
    );

    updateEventList(
        report
    );
}


/* =========================================================
   RUN RECOVERY
   ========================================================= */

async function handleRunBatch() {

    setLoading(true);

    try {

        console.log(
            "Starting Revive recovery batch..."
        );


        const report =
            await runRecoveryBatch();


        console.log(
            "Recovery report:",
            report
        );


        updateDashboard(
            report
        );


        showToast(
            "Recovery batch completed."
        );


        /*
           Move the user to the metrics
           after the batch finishes.
        */

        const metricsSection =
            document.querySelector(
                ".metrics-section"
            );


        if (metricsSection) {

            setTimeout(() => {

                metricsSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }, 250);
        }


    } catch (error) {

        console.error(
            "Recovery batch error:",
            error
        );


        showToast(
            error.message
            ||
            "Unable to run recovery batch."
        );

    } finally {

        setLoading(false);
    }
}


/* =========================================================
   INITIALIZE
   ========================================================= */

function initialize() {

    console.log(
        "Revive frontend initialized."
    );


    const buttons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn")
    ];


    buttons.forEach(button => {

        if (!button) {
            return;
        }


        button.addEventListener(
            "click",
            handleRunBatch
        );

    });
}


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);