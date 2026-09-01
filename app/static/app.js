/* =========================================================
   REVIVE — FRONTEND APPLICATION
   Recovery Run UX + Dashboard
   ========================================================= */

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
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    }).format(Number(value || 0));
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


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================================================
   TOAST
   ========================================================= */

function showToast(message) {

    const toast = $("toast");
    const messageElement = $("toastMessage");

    if (!toast || !messageElement) {
        return;
    }

    messageElement.textContent = message;

    toast.classList.add("visible");

    setTimeout(() => {
        toast.classList.remove("visible");
    }, 3000);
}


/* =========================================================
   RECOVERY RUN OVERLAY
   ========================================================= */

function createRunOverlay() {

    /*
       Create the overlay dynamically.

       This keeps the existing HTML clean and lets us
       control the complete recovery animation from JS.
    */

    if ($("recoveryOverlay")) {
        return;
    }


    const overlay = document.createElement("div");

    overlay.id = "recoveryOverlay";

    overlay.innerHTML = `
        <div class="recovery-modal">

            <div class="recovery-modal-top">

                <span class="recovery-eyebrow">
                    REVIVE ENGINE
                </span>

                <span class="recovery-live">
                    <span></span>
                    LIVE
                </span>

            </div>


            <div class="recovery-modal-content">

                <div class="recovery-orb">
                    <div class="recovery-orb-inner">
                        ✦
                    </div>
                </div>


                <h2 id="recoveryTitle">
                    Preparing recovery
                </h2>

                <p id="recoveryDescription">
                    Initializing the recovery engine...
                </p>


                <div class="recovery-progress">

                    <div
                        id="recoveryProgressBar"
                        class="recovery-progress-bar"
                    ></div>

                </div>


                <div class="recovery-steps">

                    <div
                        class="recovery-step"
                        data-step="1"
                    >
                        <span class="step-icon">
                            01
                        </span>

                        <span>
                            Analyze failures
                        </span>
                    </div>


                    <div
                        class="recovery-step"
                        data-step="2"
                    >
                        <span class="step-icon">
                            02
                        </span>

                        <span>
                            Diagnose causes
                        </span>
                    </div>


                    <div
                        class="recovery-step"
                        data-step="3"
                    >
                        <span class="step-icon">
                            03
                        </span>

                        <span>
                            Apply guardrails
                        </span>
                    </div>


                    <div
                        class="recovery-step"
                        data-step="4"
                    >
                        <span class="step-icon">
                            04
                        </span>

                        <span>
                            Execute recovery
                        </span>
                    </div>

                </div>

            </div>

        </div>
    `;


    document.body.appendChild(
        overlay
    );


    injectRecoveryStyles();
}


/* =========================================================
   RECOVERY OVERLAY STYLES
   ========================================================= */

function injectRecoveryStyles() {

    if ($("recoveryStyles")) {
        return;
    }


    const style =
        document.createElement("style");

    style.id = "recoveryStyles";

    style.textContent = `

        #recoveryOverlay {

            position: fixed;

            inset: 0;

            z-index: 1000;

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 24px;

            background: rgba(15, 15, 15, 0.55);

            backdrop-filter: blur(14px);

            opacity: 0;

            pointer-events: none;

            transition: opacity 0.25s ease;
        }


        #recoveryOverlay.visible {

            opacity: 1;

            pointer-events: auto;
        }


        .recovery-modal {

            width: min(
                620px,
                100%
            );

            padding: 28px;

            background: #ffffff;

            border: 1px solid #e5e5e1;

            border-radius: 24px;

            box-shadow:
                0 40px 120px
                rgba(0, 0, 0, 0.22);

            transform: translateY(15px)
                       scale(0.98);

            transition:
                transform 0.3s ease;
        }


        #recoveryOverlay.visible
        .recovery-modal {

            transform:
                translateY(0)
                scale(1);
        }


        .recovery-modal-top {

            display: flex;

            justify-content: space-between;

            align-items: center;
        }


        .recovery-eyebrow {

            color: #146ef5;

            font-size: 10px;

            font-weight: 700;

            letter-spacing: 0.13em;
        }


        .recovery-live {

            display: flex;

            align-items: center;

            gap: 7px;

            color: #16834b;

            font-size: 9px;

            font-weight: 700;

            letter-spacing: 0.08em;
        }


        .recovery-live span {

            width: 6px;

            height: 6px;

            border-radius: 50%;

            background: #16834b;

            animation:
                recoveryPulse
                1.2s infinite;
        }


        .recovery-modal-content {

            padding:
                55px
                25px
                25px;

            text-align: center;
        }


        .recovery-orb {

            width: 70px;

            height: 70px;

            margin: 0 auto 25px;

            display: grid;

            place-items: center;

            border-radius: 50%;

            background: #eaf2ff;

            animation:
                recoveryFloat
                2.5s ease-in-out infinite;
        }


        .recovery-orb-inner {

            width: 45px;

            height: 45px;

            display: grid;

            place-items: center;

            border-radius: 50%;

            background: #146ef5;

            color: white;

            font-size: 19px;

            box-shadow:
                0 10px 30px
                rgba(20, 110, 245, 0.25);
        }


        .recovery-modal h2 {

            font-family:
                "Manrope",
                sans-serif;

            font-size: 30px;

            line-height: 1;

            letter-spacing: -0.05em;
        }


        .recovery-modal p {

            margin-top: 10px;

            color: #777777;

            font-size: 13px;
        }


        .recovery-progress {

            height: 5px;

            margin-top: 35px;

            overflow: hidden;

            border-radius: 999px;

            background: #f1f1ee;
        }


        .recovery-progress-bar {

            width: 0;

            height: 100%;

            border-radius: inherit;

            background: #146ef5;

            transition:
                width 0.7s
                cubic-bezier(
                    0.22,
                    1,
                    0.36,
                    1
                );
        }


        .recovery-steps {

            margin-top: 30px;

            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 8px;
        }


        .recovery-step {

            padding: 13px 8px;

            border: 1px solid #e5e5e1;

            border-radius: 10px;

            color: #999999;

            font-size: 9px;

            transition:
                background 0.25s ease,
                color 0.25s ease,
                border-color 0.25s ease;
        }


        .recovery-step.active {

            border-color: #c9dbff;

            background: #eaf2ff;

            color: #146ef5;
        }


        .recovery-step.complete {

            border-color: #ccebd9;

            background: #e9f7ef;

            color: #16834b;
        }


        .step-icon {

            display: block;

            margin-bottom: 6px;

            font-size: 8px;

            font-weight: 700;
        }


        @keyframes recoveryPulse {

            0%,
            100% {
                opacity: 1;
            }

            50% {
                opacity: 0.3;
            }
        }


        @keyframes recoveryFloat {

            0%,
            100% {
                transform:
                    translateY(0);
            }

            50% {
                transform:
                    translateY(-6px);
            }
        }


        @media (max-width: 600px) {

            .recovery-modal-content {

                padding:
                    45px
                    5px
                    10px;
            }


            .recovery-steps {

                grid-template-columns:
                    repeat(2, 1fr);
            }
        }
    `;


    document.head.appendChild(
        style
    );
}


/* =========================================================
   SHOW / HIDE OVERLAY
   ========================================================= */

function showRecoveryOverlay() {

    createRunOverlay();

    const overlay =
        $("recoveryOverlay");

    requestAnimationFrame(() => {

        overlay.classList.add(
            "visible"
        );

    });
}


function hideRecoveryOverlay() {

    const overlay =
        $("recoveryOverlay");

    if (!overlay) {
        return;
    }

    overlay.classList.remove(
        "visible"
    );
}


/* =========================================================
   RECOVERY STEP ANIMATION
   ========================================================= */

function updateRecoveryStep(
    stepNumber,
    title,
    description,
    progress
) {

    $("recoveryTitle").textContent =
        title;

    $("recoveryDescription").textContent =
        description;

    $("recoveryProgressBar").style.width =
        `${progress}%`;


    document
        .querySelectorAll(".recovery-step")
        .forEach(step => {

            const number =
                Number(
                    step.dataset.step
                );

            step.classList.remove(
                "active",
                "complete"
            );


            if (
                number <
                stepNumber
            ) {

                step.classList.add(
                    "complete"
                );

            } else if (
                number ===
                stepNumber
            ) {

                step.classList.add(
                    "active"
                );
            }

        });
}


function wait(ms) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                ms
            )
    );
}


/* =========================================================
   API — RUN BATCH
   ========================================================= */

async function runRecoveryBatch() {

    const response =
        await fetch(
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
                message =
                    errorData.detail;
            }

        } catch (_) {
            // Keep default message.
        }


        throw new Error(
            message
        );
    }


    return await response.json();
}


/* =========================================================
   API — AUDIT
   ========================================================= */

async function getAuditLog(
    eventId
) {

    const response =
        await fetch(
            `${API_BASE}/audit-log/${encodeURIComponent(eventId)}`
        );


    if (!response.ok) {

        let message =
            `Audit request failed (${response.status})`;


        try {

            const errorData =
                await response.json();

            if (errorData.detail) {
                message =
                    errorData.detail;
            }

        } catch (_) {
            // Keep default message.
        }


        throw new Error(
            message
        );
    }


    return await response.json();
}


/* =========================================================
   BUTTON STATE
   ========================================================= */

function setButtonsLoading(
    isLoading
) {

    const buttons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn")
    ];


    buttons.forEach(button => {

        if (!button) {
            return;
        }


        button.disabled =
            isLoading;


        button.classList.toggle(
            "loading",
            isLoading
        );

    });
}


/* =========================================================
   METRICS
   ========================================================= */

function updateMetrics(
    report
) {

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

function updatePaymentTypePerformance(
    report
) {

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
        `${Math.min(
            oneOffRate,
            100
        )}%`;


    $("subscriptionBar").style.width =
        `${Math.min(
            subscriptionRate,
            100
        )}%`;
}


/* =========================================================
   FAILURE CATEGORIES
   ========================================================= */

function updateCategoryList(
    report
) {

    const container =
        $("categoryList");


    const categories =
        report.by_failure_category || {};


    const entries =
        Object.entries(
            categories
        );


    if (
        entries.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No category data available.
            </div>
        `;

        return;
    }


    entries.sort(
        ([, a], [, b]) =>
            Number(b.events || 0)
            -
            Number(a.events || 0)
    );


    container.innerHTML =
        entries
            .map(
                ([category, stats]) => {

                    return `
                        <div
                            class="category-item"
                        >

                            <div>

                                <div
                                    class="category-name"
                                >
                                    ${formatName(
                                        category
                                    )}
                                </div>

                                <div
                                    class="category-meta"
                                >
                                    ${stats.events || 0}
                                    events
                                    ·
                                    ${formatCurrency(
                                        stats.recovered || 0
                                    )}
                                    recovered
                                </div>

                            </div>

                            <div
                                class="category-rate"
                            >
                                ${formatPercent(
                                    stats.recovery_rate
                                )}
                            </div>

                        </div>
                    `;
                }
            )
            .join("");
}


/* =========================================================
   EVENT STATUS
   ========================================================= */

function getEventStatus(
    event
) {

    const recoveryStatus =
        event.recovery_status || "";


    const decision =
        event.decision || "";


    const status =
        event.status || "";


    if (
        recoveryStatus ===
        "recovered"
        ||
        Number(
            event.recovered_amount || 0
        ) > 0
    ) {

        return {
            label: "Recovered",
            className: "recovered"
        };
    }


    if (
        recoveryStatus ===
        "failed"
    ) {

        return {
            label: "Recovery failed",
            className: "failed"
        };
    }


    if (
        decision ===
        "escalate_to_human"
        ||
        decision ===
        "ESCALATE_TO_HUMAN"
    ) {

        return {
            label: "Escalated",
            className: "escalated"
        };
    }


    if (
        status ===
        "duplicate_skipped"
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

function updateEventList(
    report
) {

    const container =
        $("eventList");


    const events =
        report.events || [];


    $("activityCount").textContent =
        events.length;


    if (
        events.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No events available.
            </div>
        `;

        return;
    }


    const visibleEvents =
        events.slice(
            0,
            50
        );


    container.innerHTML =
        visibleEvents
            .map(
                (event, index) => {

                    const eventStatus =
                        getEventStatus(
                            event
                        );


                    return `
                        <div
                            class="event-item"
                            data-event-index="${index}"
                        >

                            <div
                                class="event-main"
                            >

                                <strong>
                                    ${formatName(
                                        event.diagnosis
                                        ||
                                        "unknown"
                                    )}
                                </strong>

                                <span>
                                    ${formatName(
                                        event.payment_type
                                        ||
                                        "unknown"
                                    )}
                                    ·
                                    ${escapeHtml(
                                        event.event_id
                                    )}
                                </span>

                                <span
                                    class="
                                        event-status
                                        ${eventStatus.className}
                                    "
                                >
                                    ${eventStatus.label}
                                </span>

                            </div>


                            <div
                                class="event-amount"
                            >
                                ${formatCurrency(
                                    event.amount
                                )}
                            </div>

                        </div>
                    `;
                }
            )
            .join("");


    container
        .querySelectorAll(
            ".event-item"
        )
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
        .querySelectorAll(
            ".event-item"
        )
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
            audit
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

function renderAuditLoading(
    event
) {

    $("auditPanel").innerHTML = `

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
    audit
) {

    const container =
        $("auditTrace");


    const entries =
        audit.audit_trail || [];


    if (
        entries.length === 0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No audit entries available.
            </div>
        `;

        return;
    }


    container.innerHTML =
        entries
            .map(
                entry => {

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


                    const data =
                        entry.data
                        ||
                        entry.metadata
                        ||
                        null;


                    if (
                        data
                        &&
                        typeof data ===
                            "object"
                    ) {

                        metadata = `
                            <pre>
${escapeHtml(
    JSON.stringify(
        data,
        null,
        2
    )
)}
                            </pre>
                        `;
                    }


                    return `
                        <div
                            class="audit-step"
                        >

                            <div
                                class="audit-dot"
                            ></div>

                            <div>

                                <strong>
                                    ${formatName(
                                        String(
                                            stage
                                        )
                                    )}
                                </strong>

                                ${
                                    detail
                                    ? `
                                        <span>
                                            ${escapeHtml(
                                                String(
                                                    detail
                                                )
                                            )}
                                        </span>
                                    `
                                    : ""
                                }

                                ${metadata}

                            </div>

                        </div>
                    `;
                }
            )
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

            ${escapeHtml(
                message
            )}

        </div>
    `;
}


/* =========================================================
   DASHBOARD UPDATE
   ========================================================= */

function updateDashboard(
    report
) {

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
   MAIN RECOVERY FLOW
   ========================================================= */

async function handleRunBatch() {

    /*
       Prevent duplicate requests.
    */

    if (
        window.reviveBatchRunning
    ) {
        return;
    }


    window.reviveBatchRunning =
        true;


    setButtonsLoading(
        true
    );


    showRecoveryOverlay();


    try {

        /* -----------------------------------------------
           STEP 1
           ----------------------------------------------- */

        updateRecoveryStep(
            1,
            "Analyzing failed payments",
            "Finding revenue at risk across the payment batch...",
            18
        );


        await wait(550);


        /* -----------------------------------------------
           STEP 2
           ----------------------------------------------- */

        updateRecoveryStep(
            2,
            "Diagnosing failure causes",
            "Classifying failures and measuring AI confidence...",
            42
        );


        await wait(550);


        /* -----------------------------------------------
           STEP 3
           ----------------------------------------------- */

        updateRecoveryStep(
            3,
            "Applying recovery guardrails",
            "Checking retry limits, economic floors and safety rules...",
            67
        );


        await wait(500);


        /* -----------------------------------------------
           ACTUAL BACKEND CALL
           ----------------------------------------------- */

        const report =
            await runRecoveryBatch();


        /* -----------------------------------------------
           STEP 4
           ----------------------------------------------- */

        updateRecoveryStep(
            4,
            "Executing eligible recovery",
            "Running approved recovery actions and recording outcomes...",
            88
        );


        await wait(650);


        /* -----------------------------------------------
           COMPLETE
           ----------------------------------------------- */

        updateRecoveryStep(
            4,
            "Recovery complete",
            `${report.events_processed || report.events?.length || 0} payment events processed successfully.`,
            100
        );


        await wait(750);


        hideRecoveryOverlay();


        updateDashboard(
            report
        );


        showToast(
            "Recovery batch completed."
        );


        /*
           Scroll to metrics.
        */

        const metrics =
            document.querySelector(
                ".metrics-section"
            );


        if (metrics) {

            setTimeout(() => {

                metrics.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }, 200);
        }


    } catch (error) {

        console.error(
            "Recovery batch error:",
            error
        );


        hideRecoveryOverlay();


        showToast(
            error.message
            ||
            "Recovery batch failed."
        );


    } finally {

        setButtonsLoading(
            false
        );


        window.reviveBatchRunning =
            false;
    }
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

function initialize() {

    console.log(
        "REVIVE frontend initialized."
    );


    const buttons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn")
    ];


    buttons.forEach(
        button => {

            if (!button) {

                console.warn(
                    "Revive: button not found."
                );

                return;
            }


            button.addEventListener(
                "click",
                handleRunBatch
            );
        }
    );


    /*
       Create overlay early so the first click
       feels instantaneous.
    */

    createRunOverlay();
}


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);