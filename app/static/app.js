/* =========================================================
   REVIVE — FRONTEND APPLICATION
   ========================================================= */


/* =========================================================
   CONFIG
   ========================================================= */

const API_BASE = "";


/* =========================================================
   DOM HELPERS
   ========================================================= */

function $(id) {
    return document.getElementById(id);
}


function setText(id, value) {
    const element = $(id);

    if (!element) {
        console.warn(`Element #${id} not found`);
        return;
    }

    element.textContent = value;
}


/* =========================================================
   FORMATTING
   ========================================================= */

function formatCurrency(value) {
    const number = Number(value || 0);

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }
    ).format(number);
}


function formatPercent(value) {
    return `${Number(value || 0).toFixed(2)}%`;
}


function formatCompactCurrency(value) {
    const number = Number(value || 0);

    if (number >= 10000000) {
        return `₹${(number / 10000000).toFixed(1)}Cr`;
    }

    if (number >= 100000) {
        return `₹${(number / 100000).toFixed(1)}L`;
    }

    if (number >= 1000) {
        return `₹${(number / 1000).toFixed(1)}K`;
    }

    return formatCurrency(number);
}


function formatName(value) {
    if (!value) {
        return "Unknown";
    }

    return String(value)
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            letter => letter.toUpperCase()
        );
}


function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
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
    const toastMessage = $("toastMessage");

    if (!toast || !toastMessage) {
        return;
    }

    toastMessage.textContent = message;

    toast.classList.add("visible");

    setTimeout(() => {
        toast.classList.remove("visible");
    }, 3500);
}


/* =========================================================
   RECOVERY OVERLAY
   ========================================================= */

function createRunOverlay() {
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
                            Analyze payments
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

    document.body.appendChild(overlay);

    injectRecoveryStyles();
}


/* =========================================================
   RECOVERY OVERLAY STYLES
   ========================================================= */

function injectRecoveryStyles() {
    if ($("recoveryStyles")) {
        return;
    }

    const style = document.createElement("style");

    style.id = "recoveryStyles";

    style.textContent = `
        #recoveryOverlay {
            position: fixed;
            inset: 0;
            z-index: 9999;

            display: flex;
            align-items: center;
            justify-content: center;

            padding: 24px;

            background: rgba(10, 12, 18, 0.62);

            backdrop-filter: blur(18px);

            opacity: 0;
            visibility: hidden;

            transition:
                opacity 0.25s ease,
                visibility 0.25s ease;
        }

        #recoveryOverlay.visible {
            opacity: 1;
            visibility: visible;
        }

        .recovery-modal {
            width: min(760px, 100%);
            max-height: 90vh;
            overflow-y: auto;

            background: #ffffff;

            border: 1px solid rgba(0, 0, 0, 0.08);

            border-radius: 28px;

            box-shadow:
                0 40px 100px
                rgba(0, 0, 0, 0.28);
        }

        .recovery-modal-top {
            display: flex;
            align-items: center;
            justify-content: space-between;

            padding: 22px 28px;

            border-bottom: 1px solid #eeeeee;
        }

        .recovery-eyebrow {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.14em;
            color: #686b75;
        }

        .recovery-live {
            display: flex;
            align-items: center;
            gap: 7px;

            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
        }

        .recovery-live span {
            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #28a745;

            animation:
                recoveryPulse
                1.2s infinite;
        }

        .recovery-modal-content {
            padding: 52px 42px 40px;
            text-align: center;
        }

        .recovery-orb {
            width: 74px;
            height: 74px;

            margin: 0 auto 26px;

            display: grid;
            place-items: center;

            border-radius: 50%;

            background: #f1f3f7;

            animation:
                recoveryFloat
                2s ease-in-out infinite;
        }

        .recovery-orb-inner {
            width: 48px;
            height: 48px;

            display: grid;
            place-items: center;

            border-radius: 50%;

            background: #111318;

            color: #ffffff;

            font-size: 22px;
        }

        #recoveryTitle {
            margin: 0 0 10px;

            font-size: clamp(25px, 4vw, 38px);

            line-height: 1.05;
        }

        #recoveryDescription {
            margin: 0 auto 30px;

            max-width: 560px;

            color: #6d707a;

            font-size: 15px;

            line-height: 1.6;
        }

        .recovery-progress {
            height: 8px;

            overflow: hidden;

            border-radius: 999px;

            background: #eeeeef;

            margin-bottom: 30px;
        }

        .recovery-progress-bar {
            width: 0%;
            height: 100%;

            border-radius: inherit;

            background: #315cf5;

            transition:
                width 0.45s ease;
        }

        .recovery-steps {
            display: grid;

            grid-template-columns:
                repeat(4, 1fr);

            gap: 12px;
        }

        .recovery-step {
            display: flex;

            flex-direction: column;

            align-items: center;

            gap: 10px;

            padding: 16px 10px;

            border: 1px solid #eeeeee;

            border-radius: 16px;

            color: #8a8d96;

            font-size: 12px;

            transition: all 0.25s ease;
        }

        .step-icon {
            width: 36px;
            height: 36px;

            display: grid;
            place-items: center;

            border-radius: 10px;

            background: #f2f2f3;

            font-size: 10px;

            font-weight: 700;
        }

        .recovery-step.active {
            color: #111318;

            border-color: #315cf5;

            background: #f5f7ff;
        }

        .recovery-step.active .step-icon {
            background: #315cf5;
            color: #ffffff;
        }

        .recovery-step.complete {
            color: #202329;

            border-color: #dfeee3;

            background: #f5faf6;
        }

        .recovery-step.complete .step-icon {
            background: #2ca24d;
            color: #ffffff;
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
                transform: translateY(0);
            }

            50% {
                transform: translateY(-6px);
            }
        }

        @media (max-width: 600px) {
            #recoveryOverlay {
                padding: 12px;
            }

            .recovery-modal-content {
                padding: 42px 18px 24px;
            }

            .recovery-steps {
                grid-template-columns:
                    repeat(2, 1fr);
            }
        }
    `;

    document.head.appendChild(style);
}


function showRecoveryOverlay() {
    createRunOverlay();

    const overlay = $("recoveryOverlay");

    requestAnimationFrame(() => {
        overlay.classList.add("visible");
    });
}


function hideRecoveryOverlay() {
    const overlay = $("recoveryOverlay");

    if (!overlay) {
        return;
    }

    overlay.classList.remove("visible");
}


function updateRecoveryStep(
    step,
    title,
    description,
    progress
) {
    const titleElement = $("recoveryTitle");
    const descriptionElement = $("recoveryDescription");
    const progressBar = $("recoveryProgressBar");

    if (titleElement) {
        titleElement.textContent = title;
    }

    if (descriptionElement) {
        descriptionElement.textContent = description;
    }

    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }

    document
        .querySelectorAll(".recovery-step")
        .forEach(element => {
            const number = Number(
                element.dataset.step
            );

            element.classList.remove(
                "active",
                "complete"
            );

            if (number < step) {
                element.classList.add(
                    "complete"
                );
            } else if (number === step) {
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
    const response = await fetch(
        `${API_BASE}/run-batch?count=10`,
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
                message = data.detail;
            }
        } catch (_) {
            // Keep default message.
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
            const data =
                await response.json();

            if (data.detail) {
                message = data.detail;
            }
        } catch (_) {
            // Keep default message.
        }

        throw new Error(message);
    }

    return await response.json();
}


/* =========================================================
   API — LATEST EXPERIMENT
   ========================================================= */

async function getLatestExperiment() {
    const response = await fetch(
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

function setButtonsLoading(loading) {
    const buttons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn"),
        $("navRunBtn")
    ];

    buttons.forEach(button => {
        if (!button) {
            return;
        }

        button.disabled = loading;

        button.classList.toggle(
            "loading",
            loading
        );
    });
}


/* =========================================================
   IMPACT METRICS
   ========================================================= */

function updateMetrics(report) {
    const atRisk = $("atRiskMetric");
    const recovered = $("recoveredMetric");
    const recoveryRate = $("recoveryRateMetric");
    const escalationRate = $("escalationRateMetric");

    if (atRisk) {
        atRisk.textContent =
            formatCurrency(
                report.total_at_risk
            );
    }

    if (recovered) {
        recovered.textContent =
            formatCurrency(
                report.total_recovered
            );
    }

    if (recoveryRate) {
        recoveryRate.textContent =
            formatPercent(
                report.recovery_rate
            );
    }

    if (escalationRate) {
        escalationRate.textContent =
            formatPercent(
                report.escalation_rate
            );
    }

    setText(
        "heroRecovered",
        formatCompactCurrency(
            report.total_recovered
        )
    );

    setText(
        "heroAtRisk",
        formatCompactCurrency(
            report.total_at_risk
        )
    );

    setText(
        "heroRecoveryRate",
        formatPercent(
            report.recovery_rate
        )
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

    setText(
        "oneOffEvents",
        `${oneOff.events || 0} events`
    );

    setText(
        "subscriptionEvents",
        `${subscription.events || 0} events`
    );

    setText(
        "oneOffRate",
        formatPercent(oneOffRate)
    );

    setText(
        "subscriptionRate",
        formatPercent(subscriptionRate)
    );

    const oneOffBar =
        $("oneOffBar");

    const subscriptionBar =
        $("subscriptionBar");

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

function updateCategoryList(report) {
    const container =
        $("categoryList");

    if (!container) {
        return;
    }

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

    entries.sort(
        ([, a], [, b]) =>
            Number(b.events || 0)
            -
            Number(a.events || 0)
    );

    container.innerHTML =
        entries
            .map(
                ([category, stats]) => `
                    <div class="category-row">

                        <div class="category-name">
                            ${escapeHtml(
                                formatName(category)
                            )}
                        </div>

                        <div class="category-events">
                            ${stats.events || 0}
                        </div>

                        <div class="category-recovered">
                            ${formatCurrency(
                                stats.recovered ??
                                stats.total_recovered ??
                                0
                            )}
                        </div>

                        <div class="category-rate">
                            ${formatPercent(
                                stats.recovery_rate
                            )}
                        </div>

                    </div>
                `
            )
            .join("");
}


/* =========================================================
   EVENT LIST
   ========================================================= */

function updateEventList(report) {
    const container =
        $("eventList");

    if (!container) {
        return;
    }

    const events =
        report.events || [];

    if (events.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No payment events available.
            </div>
        `;

        return;
    }

    container.innerHTML =
        events
            .map(
                (event, index) => {
                    const result =
                        event.result || {};

                    const diagnosis =
                        event.diagnosis || {};

                    const decision =
                        event.decision || {};

                    const status =
                        result.recovery_status
                        ||
                        result.status
                        ||
                        "not_attempted";

                    const recovered =
                        Number(
                            result.recovered_amount || 0
                        );

                    return `
                        <button
                            type="button"
                            class="event-row"
                            data-event-index="${index}"
                        >

                            <div class="event-row-main">

                                <div
                                    class="event-status-dot ${escapeHtml(
                                        status
                                    )}"
                                ></div>

                                <div>

                                    <strong>
                                        ${escapeHtml(
                                            formatName(
                                                diagnosis.category
                                                ||
                                                "unknown"
                                            )
                                        )}
                                    </strong>

                                    <span>
                                        ${escapeHtml(
                                            formatName(
                                                event.payment_type
                                                ||
                                                "payment"
                                            )
                                        )}

                                        ·

                                        ${formatCurrency(
                                            event.amount
                                        )}
                                    </span>

                                </div>

                            </div>

                            <div class="event-row-result">

                                <strong>
                                    ${
                                        recovered > 0
                                            ? formatCurrency(
                                                recovered
                                            )
                                            : formatName(
                                                status
                                            )
                                    }
                                </strong>

                                <span>
                                    ${escapeHtml(
                                        decision.action
                                        ||
                                        "no_action"
                                    )}
                                </span>

                            </div>

                        </button>
                    `;
                }
            )
            .join("");

    container
        .querySelectorAll(".event-row")
        .forEach(element => {
            element.addEventListener(
                "click",
                () => {
                    const index =
                        Number(
                            element.dataset.eventIndex
                        );

                    const event =
                        events[index];

                    selectEvent(
                        element,
                        event
                    );
                }
            );
        });
}


/* =========================================================
   SELECT EVENT
   ========================================================= */

async function selectEvent(
    element,
    event
) {
    document
        .querySelectorAll(".event-row")
        .forEach(item => {
            item.classList.remove(
                "selected"
            );
        });

    element.classList.add(
        "selected"
    );

    renderAuditLoading(event);

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

    if (!panel) {
        return;
    }

    panel.innerHTML = `
        <div class="audit-placeholder">

            <div class="placeholder-icon">
                ↻
            </div>

            <span class="eyebrow">
                EVENT INVESTIGATION
            </span>

            <h3>
                Loading audit trail
            </h3>

            <p>
                Inspecting event
                ${escapeHtml(
                    event.event_id
                )}
            </p>

        </div>
    `;
}


/* =========================================================
   AUDIT ERROR
   ========================================================= */

function renderAuditError(message) {
    const container =
        $("auditPanel");

    if (!container) {
        return;
    }

    container.innerHTML = `
        <div class="audit-placeholder">

            <div class="placeholder-icon">
                !
            </div>

            <span class="eyebrow">
                AUDIT ERROR
            </span>

            <h3>
                Unable to load audit trail
            </h3>

            <p>
                ${escapeHtml(message)}
            </p>

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
        $("auditPanel");

    if (!container) {
        return;
    }

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

    const diagnosisCategory =
        event.diagnosis?.category
        ||
        event.diagnosis
        ||
        "Unknown";

    container.innerHTML = `
        <div class="trace-summary">

            <div class="trace-summary-item">

                <span>
                    Diagnosis
                </span>

                <strong>
                    ${escapeHtml(
                        formatName(
                            diagnosisCategory
                        )
                    )}
                </strong>

            </div>

            <div class="trace-summary-item">

                <span>
                    Amount
                </span>

                <strong>
                    ${formatCurrency(
                        event.amount
                    )}
                </strong>

            </div>

            <div class="trace-summary-item">

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
                                metadata &&
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
                                        class="trace-content"
                                    >

                                        <span
                                            class="trace-stage"
                                        >
                                            ${escapeHtml(
                                                formatName(
                                                    stage
                                                )
                                            )}
                                        </span>

                                        <strong>
                                            ${escapeHtml(
                                                formatName(
                                                    eventName
                                                )
                                            )}
                                        </strong>

                                        <p>
                                            ${escapeHtml(
                                                detail
                                            )}
                                        </p>

                                        ${metadataHtml}

                                    </div>

                                </div>
                            `;
                        }
                    )
                    .join("")
            }

        </div>
    `;
}


/* =========================================================
   AUDIT HELPERS
   ========================================================= */

function identifyStage(
    entry,
    index
) {
    if (entry.stage) {
        return entry.stage;
    }

    const stages = [
        "RECEIVED",
        "VALIDATED",
        "DIAGNOSING",
        "DIAGNOSED",
        "DECIDING",
        "DECIDED",
        "EXECUTING",
        "ESCALATED",
        "STOPPED",
        "COMPLETED"
    ];

    return stages[index] || "EVENT";
}


function getEntryDetail(entry) {
    const details =
        entry.details;

    if (!details) {
        return (
            entry.reasoning
            ||
            entry.message
            ||
            "Stage recorded in audit trail."
        );
    }

    if (typeof details === "string") {
        return details;
    }

    if (details.reasoning) {
        return details.reasoning;
    }

    if (details.reason) {
        return `Decision reason: ${
            formatName(
                details.reason
            )
        }`;
    }

    if (details.action) {
        return `Action: ${
            formatName(
                details.action
            )
        }`;
    }

    if (details.execution_result) {
        return "Execution result recorded.";
    }

    return "Stage recorded in audit trail.";
}


function getEntryMetadata(entry) {
    if (
        !entry.details
        ||
        typeof entry.details !==
            "object"
    ) {
        return null;
    }

    return entry.details;
}


/* =========================================================
   DASHBOARD UPDATE
   ========================================================= */

function updateDashboard(report) {
    updateMetrics(report);

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

        /* ---------------------------------------------
           BASELINE
        --------------------------------------------- */

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

        /* ---------------------------------------------
           REVIVE
        --------------------------------------------- */

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

        /* ---------------------------------------------
           INSIGHT
        --------------------------------------------- */

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
    if (window.reviveBatchRunning) {
        return;
    }

    window.reviveBatchRunning = true;

    setButtonsLoading(true);

    /*
       Start overlay immediately.
    */

    showRecoveryOverlay();

    try {
        /* ---------------------------------------------
           STEP 1
        --------------------------------------------- */

        updateRecoveryStep(
            1,
            "Analyzing failed payments",
            "Finding revenue at risk across the payment batch...",
            18
        );

        /*
           Start real backend request.
        */

        const batchPromise =
            runRecoveryBatch();

        await wait(550);

        /* ---------------------------------------------
           STEP 2
        --------------------------------------------- */

        updateRecoveryStep(
            2,
            "Diagnosing failure causes",
            "Classifying payment failures and estimating confidence...",
            38
        );

        await wait(650);

        /* ---------------------------------------------
           STEP 3
        --------------------------------------------- */

        updateRecoveryStep(
            3,
            "Applying deterministic guardrails",
            "Checking economics, confidence, retry limits and fraud protection...",
            62
        );

        await wait(650);

        /* ---------------------------------------------
           STEP 4
        --------------------------------------------- */

        updateRecoveryStep(
            4,
            "Executing eligible recovery",
            "Running approved recovery actions and recording outcomes...",
            88
        );

        /*
           Wait for actual backend result.
        */

        const report =
            await batchPromise;

        await wait(400);

        /* ---------------------------------------------
           COMPLETE
        --------------------------------------------- */

        updateRecoveryStep(
            4,
            "Recovery complete",
            `${report.events_processed || report.events?.length || 0} payment events processed.`,
            100
        );

        await wait(900);

        hideRecoveryOverlay();

        /*
           Update dashboard.
        */

        updateDashboard(
            report
        );

        /*
           Reload experiment comparison.
        */

        await loadExperimentComparison();

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
        setButtonsLoading(false);

        window.reviveBatchRunning =
            false;
    }
}


/* =========================================================
   NAVIGATION
   ========================================================= */

function initializeNavigation() {
    document
        .querySelectorAll(".nav-link")
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

    const navRunBtn =
        $("navRunBtn");

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