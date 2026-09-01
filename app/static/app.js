/* =========================================================
   REVIVE
   Revenue Recovery Intelligence
   Frontend Application
   ========================================================= */

const API_BASE = "";


/* =========================================================
   DOM HELPER
   ========================================================= */

function $(id) {
    return document.getElementById(id);
}


/* =========================================================
   FORMATTING
   ========================================================= */

function formatCurrency(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(
        Number(value || 0)
    );
}


function formatPercent(value) {

    return `${Number(
        value || 0
    ).toFixed(2)}%`;
}


function formatName(value) {

    if (!value) {
        return "Unknown";
    }

    return String(value)
        .replaceAll("_", " ")
        .replace(/\b\w/g, letter =>
            letter.toUpperCase()
        );
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

    const toast =
        $("toast");

    const messageElement =
        $("toastMessage");


    if (
        !toast ||
        !messageElement
    ) {
        return;
    }


    messageElement.textContent =
        message;


    toast.classList.add(
        "visible"
    );


    setTimeout(() => {

        toast.classList.remove(
            "visible"
        );

    }, 3000);
}


/* =========================================================
   RECOVERY OVERLAY
   ========================================================= */

function createRunOverlay() {

    if (
        $("recoveryOverlay")
    ) {
        return;
    }


    const overlay =
        document.createElement(
            "div"
        );


    overlay.id =
        "recoveryOverlay";


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
                    Initializing recovery engine...
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

    if (
        $("recoveryStyles")
    ) {
        return;
    }


    const style =
        document.createElement(
            "style"
        );


    style.id =
        "recoveryStyles";


    style.textContent = `

        #recoveryOverlay {

            position: fixed;

            inset: 0;

            z-index: 1000;

            display: flex;

            align-items: center;

            justify-content: center;

            padding: 24px;

            background:
                rgba(15, 15, 15, 0.55);

            backdrop-filter:
                blur(14px);

            opacity: 0;

            pointer-events: none;

            transition:
                opacity 0.25s ease;
        }


        #recoveryOverlay.visible {

            opacity: 1;

            pointer-events: auto;
        }


        .recovery-modal {

            width:
                min(620px, 100%);

            padding: 28px;

            background: #ffffff;

            border:
                1px solid #e5e5e1;

            border-radius: 24px;

            box-shadow:
                0 40px 120px
                rgba(0, 0, 0, 0.22);

            transform:
                translateY(15px)
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

            justify-content:
                space-between;

            align-items: center;
        }


        .recovery-eyebrow {

            color: #146ef5;

            font-size: 10px;

            font-weight: 700;

            letter-spacing:
                0.13em;
        }


        .recovery-live {

            display: flex;

            align-items: center;

            gap: 7px;

            color: #16834b;

            font-size: 9px;

            font-weight: 700;

            letter-spacing:
                0.08em;
        }


        .recovery-live span {

            width: 6px;

            height: 6px;

            border-radius: 50%;

            background: #16834b;

            animation:
                recoveryPulse 1.2s
                infinite;
        }


        .recovery-modal-content {

            padding:
                55px 25px 25px;

            text-align: center;
        }


        .recovery-orb {

            width: 70px;

            height: 70px;

            margin:
                0 auto 25px;

            display: grid;

            place-items: center;

            border-radius: 50%;

            background: #eaf2ff;

            animation:
                recoveryFloat 2.5s
                ease-in-out infinite;
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

            letter-spacing:
                -0.05em;
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

            border:
                1px solid #e5e5e1;

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
                    45px 5px 10px;
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


function updateRecoveryStep(
    step,
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
        .querySelectorAll(
            ".recovery-step"
        )
        .forEach(element => {

            const number =
                Number(
                    element.dataset.step
                );


            element.classList.remove(
                "active",
                "complete"
            );


            if (
                number < step
            ) {

                element.classList.add(
                    "complete"
                );

            } else if (
                number === step
            ) {

                element.classList.add(
                    "active"
                );
            }

        });
}


function wait(milliseconds) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
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

            const data =
                await response.json();


            if (data.detail) {

                message =
                    data.detail;
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
   API — AUDIT LOG
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

            const data =
                await response.json();


            if (data.detail) {

                message =
                    data.detail;
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
   API — LATEST EXPERIMENT
   ========================================================= */

async function getLatestExperiment() {

    const response =
        await fetch(
            "/experiment/latest"
        );


    if (!response.ok) {

        throw new Error(
            "No experiment results available."
        );
    }


    return await response.json();
}


/* =========================================================
   BUTTON STATE
   ========================================================= */

function setButtonsLoading(
    loading
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
            loading;


        button.classList.toggle(
            "loading",
            loading
        );

    });
}


/* =========================================================
   IMPACT METRICS
   ========================================================= */

function updateMetrics(
    report
) {

    if (
        $("atRiskMetric")
    ) {

        $("atRiskMetric").textContent =
            formatCurrency(
                report.total_at_risk
            );
    }


    if (
        $("recoveredMetric")
    ) {

        $("recoveredMetric").textContent =
            formatCurrency(
                report.total_recovered
            );
    }


    if (
        $("recoveryRateMetric")
    ) {

        $("recoveryRateMetric").textContent =
            formatPercent(
                report.recovery_rate
            );
    }


    if (
        $("escalationRateMetric")
    ) {

        $("escalationRateMetric").textContent =
            formatPercent(
                report.escalation_rate
            );
    }
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


    const oneOffEvents =
        $("oneOffEvents");


    const subscriptionEvents =
        $("subscriptionEvents");


    const oneOffRateElement =
        $("oneOffRate");


    const subscriptionRateElement =
        $("subscriptionRate");


    const oneOffBar =
        $("oneOffBar");


    const subscriptionBar =
        $("subscriptionBar");


    if (oneOffEvents) {

        oneOffEvents.textContent =
            `${oneOff.events || 0} events`;
    }


    if (subscriptionEvents) {

        subscriptionEvents.textContent =
            `${subscription.events || 0} events`;
    }


    if (oneOffRateElement) {

        oneOffRateElement.textContent =
            formatPercent(
                oneOffRate
            );
    }


    if (subscriptionRateElement) {

        subscriptionRateElement.textContent =
            formatPercent(
                subscriptionRate
            );
    }


    if (oneOffBar) {

        oneOffBar.style.width =
            `${Math.min(
                oneOffRate,
                100
            )}%`;
    }


    if (subscriptionBar) {

        subscriptionBar.style.width =
            `${Math.min(
                subscriptionRate,
                100
            )}%`;
    }
}


/* =========================================================
   FAILURE CATEGORIES
   ========================================================= */

function updateCategoryList(
    report
) {

    const container =
        $("categoryList");


    if (!container) {
        return;
    }


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
            Number(
                b.events || 0
            )
            -
            Number(
                a.events || 0
            )
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

    const status =
        event.recovery_status || "";


    const decision =
        event.decision || "";


    if (
        status === "recovered"
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
        status === "failed"
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


    if (!container) {
        return;
    }


    const events =
        report.events || [];


    const count =
        $("activityCount");


    if (count) {

        count.textContent =
            events.length;
    }


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

                    const status =
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

                                <div
                                    class="event-title-row"
                                >

                                    <strong>
                                        ${formatName(
                                            event.diagnosis
                                            ||
                                            "unknown"
                                        )}
                                    </strong>

                                    <span
                                        class="
                                            event-status
                                            ${status.className}
                                        "
                                    >
                                        ${status.label}
                                    </span>

                                </div>


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
   EVENT INVESTIGATION HEADER
   ========================================================= */

function renderAuditLoading(
    event
) {

    const panel =
        $("auditPanel");


    if (!panel) {
        return;
    }


    panel.innerHTML = `

        <div class="trace-header">

            <div
                class="trace-header-top"
            >

                <div>

                    <div
                        class="trace-eyebrow"
                    >
                        PAYMENT INVESTIGATION
                    </div>


                    <h3>
                        ${formatCurrency(
                            event.amount
                        )}
                    </h3>


                    <p>
                        ${escapeHtml(
                            event.event_id
                        )}
                    </p>

                </div>


                <div
                    class="trace-payment-type"
                >
                    ${formatName(
                        event.payment_type
                    )}
                </div>

            </div>


            <div
                class="trace-failure"
            >

                <span
                    class="trace-failure-label"
                >
                    FAILURE
                </span>


                <strong>

                    ${escapeHtml(
                        event.failure_message
                        ||
                        "Payment failed"
                    )}

                </strong>

            </div>

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
   AUDIT STAGE
   ========================================================= */

function identifyStage(
    entry,
    index
) {

    const raw =
        String(
            entry.stage
            ||
            entry.state
            ||
            entry.event
            ||
            entry.action
            ||
            ""
        ).toLowerCase();


    if (
        raw.includes("diagnos")
    ) {

        return "AI DIAGNOSIS";
    }


    if (
        raw.includes("policy")
        ||
        raw.includes("decision")
        ||
        raw.includes("deciding")
    ) {

        return "POLICY ENGINE";
    }


    if (
        raw.includes("execut")
        ||
        raw.includes("retry")
    ) {

        return "RECOVERY ACTION";
    }


    if (
        raw.includes("escalat")
    ) {

        return "ESCALATION";
    }


    if (
        raw.includes("complet")
        ||
        raw.includes("recover")
    ) {

        return "OUTCOME";
    }


    if (
        raw.includes("valid")
        ||
        raw.includes("received")
        ||
        raw.includes("payment")
    ) {

        return "PAYMENT";
    }


    const fallbackStages = [

        "PAYMENT",

        "AI DIAGNOSIS",

        "POLICY ENGINE",

        "RECOVERY ACTION",

        "OUTCOME"

    ];


    return (
        fallbackStages[index]
        ||
        "RECOVERY EVENT"
    );
}


/* =========================================================
   AUDIT DETAIL
   ========================================================= */

function getEntryDetail(
    entry
) {

    return (
        entry.detail
        ||
        entry.message
        ||
        entry.reason
        ||
        entry.description
        ||
        ""
    );
}


/* =========================================================
   AUDIT METADATA
   ========================================================= */

function getEntryMetadata(
    entry
) {

    return (
        entry.data
        ||
        entry.metadata
        ||
        entry.details
        ||
        null
    );
}


/* =========================================================
   RENDER AUDIT TRACE
   ========================================================= */

function renderAuditTrace(
    audit,
    event
) {

    const container =
        $("auditTrace");


    if (!container) {
        return;
    }


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


    container.innerHTML = `

        <div class="trace-summary">


            <div
                class="trace-summary-item"
            >

                <span>
                    Diagnosis
                </span>

                <strong>

                    ${formatName(
                        event.diagnosis
                        ||
                        "Unknown"
                    )}

                </strong>

            </div>


            <div
                class="trace-summary-item"
            >

                <span>
                    Amount
                </span>

                <strong>

                    ${formatCurrency(
                        event.amount
                    )}

                </strong>

            </div>


            <div
                class="trace-summary-item"
            >

                <span>
                    Retry count
                </span>

                <strong>

                    ${event.retry_count ?? 0}

                </strong>

            </div>


        </div>


        <div class="trace-title">

            Recovery decision trail

        </div>


        <div class="trace-timeline">


            ${
                entries
                    .map(
                        (entry, index) => {

                            const stage =
                                identifyStage(
                                    entry,
                                    index
                                );


                            const detail =
                                getEntryDetail(
                                    entry
                                );


                            const metadata =
                                getEntryMetadata(
                                    entry
                                );


                            let metadataHtml =
                                "";


                            if (
                                metadata
                                &&
                                typeof metadata ===
                                    "object"
                            ) {

                                metadataHtml = `

                                    <details
                                        class="trace-data"
                                    >

                                        <summary>
                                            View event data
                                        </summary>

                                        <pre>${escapeHtml(
                                            JSON.stringify(
                                                metadata,
                                                null,
                                                2
                                            )
                                        )}</pre>

                                    </details>

                                `;
                            }


                            const eventName =
                                entry.action
                                ||
                                entry.event
                                ||
                                entry.stage
                                ||
                                stage;


                            return `

                                <div
                                    class="trace-event"
                                >


                                    <div
                                        class="trace-marker"
                                    >

                                        <span>

                                            ${String(
                                                index + 1
                                            ).padStart(
                                                2,
                                                "0"
                                            )}

                                        </span>

                                    </div>


                                    <div
                                        class="trace-event-content"
                                    >

                                        <div
                                            class="trace-event-label"
                                        >

                                            ${stage}

                                        </div>


                                        <div
                                            class="trace-event-card"
                                        >

                                            <strong>

                                                ${formatName(
                                                    String(
                                                        eventName
                                                    )
                                                )}

                                            </strong>


                                            ${
                                                detail
                                                ? `

                                                    <p>

                                                        ${escapeHtml(
                                                            String(
                                                                detail
                                                            )
                                                        )}

                                                    </p>

                                                `
                                                : ""
                                            }


                                            ${metadataHtml}

                                        </div>


                                    </div>


                                </div>

                            `;
                        }
                    )
                    .join("")
            }


        </div>

    `;


    injectTraceStyles();
}


/* =========================================================
   TRACE STYLES
   ========================================================= */

function injectTraceStyles() {

    if (
        $("traceStyles")
    ) {
        return;
    }


    const style =
        document.createElement(
            "style"
        );


    style.id =
        "traceStyles";


    style.textContent = `

        .trace-header {

            padding-bottom: 24px;

            border-bottom:
                1px solid #e5e5e1;
        }


        .trace-header-top {

            display: flex;

            justify-content:
                space-between;

            align-items:
                flex-start;

            gap: 20px;
        }


        .trace-eyebrow {

            color: #146ef5;

            font-size: 9px;

            font-weight: 700;

            letter-spacing:
                0.12em;
        }


        .trace-header h3 {

            margin-top: 8px;

            font-family:
                "Manrope",
                sans-serif;

            font-size: 30px;

            letter-spacing:
                -0.05em;
        }


        .trace-header p {

            margin-top: 3px;

            color: #999999;

            font-size: 10px;
        }


        .trace-payment-type {

            padding:
                7px 10px;

            border:
                1px solid #e5e5e1;

            border-radius:
                999px;

            color: #666666;

            font-size: 9px;

            font-weight: 600;
        }


        .trace-failure {

            margin-top: 20px;

            padding: 15px;

            border-radius: 12px;

            background: #fff5f5;

            border:
                1px solid #f1dddd;
        }


        .trace-failure-label {

            display: block;

            color: #c13d3d;

            font-size: 8px;

            font-weight: 700;

            letter-spacing:
                0.1em;
        }


        .trace-failure strong {

            display: block;

            margin-top: 5px;

            color: #5e3333;

            font-size: 12px;

            line-height: 1.4;
        }


        .trace-summary {

            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap: 8px;

            margin-top: 25px;
        }


        .trace-summary-item {

            padding: 13px;

            background: #f1f1ee;

            border-radius: 10px;
        }


        .trace-summary-item span {

            display: block;

            color: #999999;

            font-size: 9px;
        }


        .trace-summary-item strong {

            display: block;

            margin-top: 5px;

            font-size: 11px;
        }


        .trace-title {

            margin-top: 30px;

            margin-bottom: 18px;

            font-size: 11px;

            font-weight: 700;

            text-transform: uppercase;

            letter-spacing:
                0.08em;
        }


        .trace-timeline {

            display: flex;

            flex-direction:
                column;
        }


        .trace-event {

            display: grid;

            grid-template-columns:
                35px 1fr;

            gap: 15px;

            min-height: 78px;
        }


        .trace-marker {

            position: relative;

            display: flex;

            justify-content:
                center;
        }


        .trace-marker::after {

            content: "";

            position: absolute;

            top: 27px;

            bottom: -1px;

            width: 1px;

            background: #e5e5e1;
        }


        .trace-event:last-child
        .trace-marker::after {

            display: none;
        }


        .trace-marker span {

            position: relative;

            z-index: 2;

            width: 25px;

            height: 25px;

            display: grid;

            place-items: center;

            border-radius: 50%;

            background: #eaf2ff;

            color: #146ef5;

            font-size: 8px;

            font-weight: 700;
        }


        .trace-event-label {

            margin-bottom: 6px;

            color: #999999;

            font-size: 8px;

            font-weight: 700;

            letter-spacing:
                0.08em;
        }


        .trace-event-card {

            padding:
                12px 14px;

            border:
                1px solid #e5e5e1;

            border-radius: 10px;

            background: #ffffff;
        }


        .trace-event-card strong {

            font-size: 11px;
        }


        .trace-event-card p {

            margin-top: 5px;

            color: #777777;

            font-size: 10px;

            line-height: 1.5;
        }


        .trace-data {

            margin-top: 10px;

            color: #999999;

            font-size: 9px;
        }


        .trace-data summary {

            cursor: pointer;
        }


        .trace-data pre {

            margin-top: 7px;

            padding: 10px;

            overflow-x: auto;

            background: #f1f1ee;

            border-radius: 7px;

            font-size: 8px;
        }


        @media (max-width: 600px) {

            .trace-summary {

                grid-template-columns:
                    1fr;
            }


            .trace-header-top {

                flex-direction:
                    column;
            }

        }

    `;


    document.head.appendChild(
        style
    );
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
   EXPERIMENT COMPARISON
   ========================================================= */

async function loadExperimentComparison() {

    try {

        const experiment =
            await getLatestExperiment();


        const baseline =
            experiment.baseline || {};


        const revive =
            experiment.revive || {};


        const comparison =
            experiment.comparison || {};


        /*
           BASELINE
        */

        const baselineRecovered =
            $("baselineRecovered");


        if (baselineRecovered) {

            baselineRecovered.textContent =
                formatCurrency(
                    baseline.total_recovered
                );
        }


        const baselineRate =
            $("baselineRecoveryRate");


        if (baselineRate) {

            baselineRate.textContent =
                formatPercent(
                    baseline.recovery_rate
                );
        }


        const baselineUnsafe =
            $("baselineUnsafeRetries");


        if (baselineUnsafe) {

            baselineUnsafe.textContent =
                baseline.unsafe_retry_count
                ??
                baseline.unsafe_retries
                ??
                0;
        }


        /*
           REVIVE
        */

        const reviveRecovered =
            $("reviveRecovered");


        if (reviveRecovered) {

            reviveRecovered.textContent =
                formatCurrency(
                    revive.total_recovered
                );
        }


        const reviveRate =
            $("reviveRecoveryRate");


        if (reviveRate) {

            reviveRate.textContent =
                formatPercent(
                    revive.recovery_rate
                );
        }


        const reviveUnsafe =
            $("reviveUnsafeRetries");


        if (reviveUnsafe) {

            reviveUnsafe.textContent =
                comparison.revive_unsafe_retries
                ??
                0;
        }


        /*
           INSIGHT
        */

        const insight =
            $("comparisonInsight");


        if (insight) {

            const unsafe =
                comparison.baseline_unsafe_retries
                ??
                baseline.unsafe_retry_count
                ??
                0;


            insight.textContent =
                `Revive prevented ${unsafe} unsafe retry actions while maintaining controlled recovery.`;
        }


    } catch (error) {

        console.warn(
            "Experiment comparison unavailable:",
            error
        );

    }
}


/* =========================================================
   MAIN RECOVERY FLOW
   ========================================================= */

async function handleRunBatch() {

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

        /*
           STEP 1
        */

        updateRecoveryStep(
            1,
            "Analyzing failed payments",
            "Finding revenue at risk across the payment batch...",
            18
        );


        await wait(550);


        /*
           STEP 2
        */

        updateRecoveryStep(
            2,
            "Diagnosing failure causes",
            "Classifying failures and measuring AI confidence...",
            42
        );


        await wait(550);


        /*
           STEP 3
        */

        updateRecoveryStep(
            3,
            "Applying recovery guardrails",
            "Checking retry limits, economic floors and safety rules...",
            67
        );


        await wait(500);


        /*
           REAL BACKEND CALL
        */

        const report =
            await runRecoveryBatch();


        /*
           STEP 4
        */

        updateRecoveryStep(
            4,
            "Executing eligible recovery",
            "Running approved recovery actions and recording outcomes...",
            88
        );


        await wait(650);


        /*
           COMPLETE
        */

        updateRecoveryStep(
            4,
            "Recovery complete",
            `${report.events_processed || report.events?.length || 0} payment events processed.`,
            100
        );


        await wait(750);


        hideRecoveryOverlay();


        updateDashboard(
            report
        );


        /*
           Reload experiment data in case
           a fresh experiment was generated.
        */

        loadExperimentComparison();


        showToast(
            "Recovery batch completed."
        );


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
   NAVIGATION
   ========================================================= */

function initializeNavigation() {

    document
        .querySelectorAll(
            ".nav-link"
        )
        .forEach(link => {

            link.addEventListener(
                "click",
                () => {

                    document
                        .querySelectorAll(
                            ".nav-link"
                        )
                        .forEach(
                            navLink =>
                                navLink.classList.remove(
                                    "active"
                                )
                        );


                    link.classList.add(
                        "active"
                    );

                }
            );

        });
}


/* =========================================================
   INITIALIZATION
   ========================================================= */

function initialize() {

    console.log(
        "REVIVE frontend initialized."
    );

    const navRunBtn = $("navRunBtn");

if (navRunBtn) {
    navRunBtn.addEventListener(
        "click",
        handleRunBatch
    );
}


    const buttons = [

        $("runBatchBtn"),

        $("heroRunBtn"),

        $("finalRunBtn")

    ];


    buttons.forEach(button => {

        if (!button) {

            console.warn(
                "Revive button not found."
            );

            return;
        }


        button.addEventListener(
            "click",
            handleRunBatch
        );

    });


    createRunOverlay();


    loadExperimentComparison();


    initializeNavigation();
}


/* =========================================================
   START
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);