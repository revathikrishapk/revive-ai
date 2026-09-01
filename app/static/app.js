/* =========================================================
   REVIVE — FRONTEND APPLICATION
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

    if (element) {
        element.textContent = value;
    }
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
   ENGINE MODAL
   Uses the existing engineModal from index.html.
========================================================= */

const ENGINE_STAGES = [
    {
        key: "ingestion",
        title: "Receiving payment events",
        description:
            "Ingesting the failed payment batch...",
        progress: 12,
    },

    {
        key: "validation",
        title: "Validating payment events",
        description:
            "Checking payment contracts before processing...",
        progress: 24,
    },

    {
        key: "diagnosis",
        title: "Running OpenRouter AI diagnosis",
        description:
            "Classifying likely payment failure causes...",
        progress: 48,
    },

    {
        key: "policy",
        title: "Applying deterministic guardrails",
        description:
            "Checking economic floor, confidence, retry limits and fraud protection...",
        progress: 68,
    },

    {
        key: "execution",
        title: "Executing eligible recovery",
        description:
            "Running only actions approved by deterministic policy...",
        progress: 86,
    },

    {
        key: "audit",
        title: "Recording audit trail",
        description:
            "Persisting every recovery decision and outcome...",
        progress: 96,
    },
];


function openEngineModal() {
    const modal = $("engineModal");

    if (!modal) {
        return;
    }

    resetEngineModal();

    modal.classList.add("is-open");

    modal.setAttribute(
        "aria-hidden",
        "false"
    );
}


function closeEngineModal() {
    const modal = $("engineModal");

    if (!modal) {
        return;
    }

    modal.classList.remove("is-open");

    modal.setAttribute(
        "aria-hidden",
        "true"
    );
}


function resetEngineModal() {

    setText(
        "engineModalTitle",
        "Processing payments"
    );

    setText(
        "engineModalSubtitle",
        "Running the Revive recovery pipeline."
    );

    setText(
        "engineProgressLabel",
        "Preparing engine..."
    );

    setText(
        "engineProgressCount",
        "0%"
    );


    const progressBar =
        $("engineProgressBar");

    if (progressBar) {
        progressBar.style.width = "0%";
    }


    const result =
        $("engineResult");

    if (result) {
        result.classList.remove(
            "visible"
        );
    }


    const doneButton =
        $("engineDoneBtn");

    if (doneButton) {

        doneButton.style.display =
            "none";

        doneButton.textContent =
            "Done";
    }


    document
        .querySelectorAll(
            ".engine-stage"
        )
        .forEach(stage => {

            stage.classList.remove(
                "active",
                "complete"
            );

        });
}


function updateEngineStage(
    stageKey,
    progressOverride = null
) {

    const stageIndex =
        ENGINE_STAGES.findIndex(
            stage =>
                stage.key === stageKey
        );

    if (stageIndex === -1) {
        return;
    }


    const stage =
        ENGINE_STAGES[stageIndex];


    const progress =
        progressOverride ??
        stage.progress;


    setText(
        "engineModalTitle",
        stage.title
    );

    setText(
        "engineModalSubtitle",
        stage.description
    );

    setText(
        "engineProgressLabel",
        stage.title
    );

    setText(
        "engineProgressCount",
        `${progress}%`
    );


    const progressBar =
        $("engineProgressBar");

    if (progressBar) {

        progressBar.style.width =
            `${progress}%`;

    }


    document
        .querySelectorAll(
            ".engine-stage"
        )
        .forEach(element => {

            const key =
                element.dataset.stage;

            const currentIndex =
                ENGINE_STAGES.findIndex(
                    item =>
                        item.key === key
                );


            element.classList.remove(
                "active",
                "complete"
            );


            if (
                currentIndex <
                stageIndex
            ) {

                element.classList.add(
                    "complete"
                );

            } else if (
                currentIndex ===
                stageIndex
            ) {

                element.classList.add(
                    "active"
                );
            }

        });
}


function completeEngineModal(report) {

    document
        .querySelectorAll(
            ".engine-stage"
        )
        .forEach(stage => {

            stage.classList.remove(
                "active"
            );

            stage.classList.add(
                "complete"
            );

        });


    setText(
        "engineModalTitle",
        "Recovery batch complete"
    );


    setText(
        "engineModalSubtitle",
        `${
            report.events_processed ||
            report.events?.length ||
            0
        } payment events processed successfully.`
    );


    setText(
        "engineProgressLabel",
        "Complete"
    );


    setText(
        "engineProgressCount",
        "100%"
    );


    const progressBar =
        $("engineProgressBar");

    if (progressBar) {
        progressBar.style.width =
            "100%";
    }


    setText(
        "engineRecovered",
        formatCurrency(
            report.total_recovered
        )
    );


    setText(
        "engineRecoveryRate",
        formatPercent(
            report.recovery_rate
        )
    );


    setText(
        "engineEvents",
        report.events_processed ||
        report.events?.length ||
        0
    );


    const result =
        $("engineResult");

    if (result) {
        result.classList.add(
            "visible"
        );
    }


    const doneButton =
        $("engineDoneBtn");

    if (doneButton) {

        doneButton.style.display =
            "inline-flex";

        doneButton.textContent =
            "Done";
    }
}


function failEngineModal(error) {

    document
        .querySelectorAll(
            ".engine-stage"
        )
        .forEach(stage => {

            stage.classList.remove(
                "active"
            );

        });


    setText(
        "engineModalTitle",
        "Recovery batch failed"
    );


    setText(
        "engineModalSubtitle",
        error?.message ||
        "The recovery engine could not complete the batch."
    );


    setText(
        "engineProgressLabel",
        "Failed"
    );


    const doneButton =
        $("engineDoneBtn");

    if (doneButton) {

        doneButton.style.display =
            "inline-flex";

        doneButton.textContent =
            "Close";
    }
}


/* =========================================================
   API — RUN BATCH
========================================================= */

async function runRecoveryBatch() {

    /*
       Backend supports 1–500 events.
       The dashboard uses 80 for a normal
       interactive recovery run.
    */

    const response =
        await fetch(
            `${API_BASE}/run-batch?count=80`,
            {
                method: "POST",
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

async function getAuditLog(eventId) {

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
            `${API_BASE}/experiment/latest`
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
        $("finalRunBtn"),
        $("navRunBtn"),
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

function updateMetrics(report) {

    setText(
        "atRiskMetric",
        formatCurrency(
            report.total_at_risk
        )
    );


    setText(
        "recoveredMetric",
        formatCurrency(
            report.total_recovered
        )
    );


    setText(
        "recoveryRateMetric",
        formatPercent(
            report.recovery_rate
        )
    );


    setText(
        "escalationRateMetric",
        formatPercent(
            report.escalation_rate
        )
    );


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
   FAILURE CATEGORIES
========================================================= */

function updateCategoryList(report) {

    const container =
        $("categoryList");


    if (!container) {
        return;
    }


    const categories =
        report.by_failure_category ||
        {};


    const entries =
        Object.entries(
            categories
        );


    if (
        entries.length ===
        0
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
            ) -
            Number(
                a.events || 0
            )
    );


    container.innerHTML =
        entries
            .map(
                ([category, stats]) => `

                    <div class="category-row">

                        <div class="category-name">

                            ${escapeHtml(
                                formatName(
                                    category
                                )
                            )}

                        </div>


                        <div class="category-events">

                            ${Number(
                                stats.events || 0
                            )}

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
   EVENT STATUS
========================================================= */
/* =========================================================
   EVENT NORMALIZATION
   Backend returns flat event summaries.
   Frontend uses nested objects.
========================================================= */

function normalizeEvent(rawEvent) {

    if (!rawEvent) {
        return {};
    }

    return {
        ...rawEvent,

        diagnosis:
            rawEvent.diagnosis &&
            typeof rawEvent.diagnosis === "object"
                ? rawEvent.diagnosis
                : {
                    category:
                        rawEvent.diagnosis ||
                        "unknown",

                    confidence:
                        rawEvent.confidence ??
                        0,

                    reasoning:
                        rawEvent.reasoning ||
                        "",
                },

        decision:
            rawEvent.decision &&
            typeof rawEvent.decision === "object"
                ? rawEvent.decision
                : {
                    action:
                        rawEvent.decision ||
                        "no_action",

                    reason:
                        rawEvent.decision_reason ||
                        "unknown",

                    retry_cadence:
                        rawEvent.retry_cadence ||
                        "none",
                },

        result:
            rawEvent.result &&
            typeof rawEvent.result === "object"
                ? rawEvent.result
                : {
                    status:
                        rawEvent.status ||
                        "not_executed",

                    recovery_status:
                        rawEvent.recovery_status ||
                        "not_attempted",

                    recovered_amount:
                        rawEvent.recovered_amount ||
                        0,
                },
    };
}





function getEventStatus(event) {

    const result =
        event.result || {};


    const decision =
        event.decision || {};


    if (
        result.recovery_status ===
        "recovered"
    ) {

        return "recovered";
    }


    if (
        result.recovery_status ===
        "failed"
    ) {

        return "failed";
    }


    if (
        decision.action ===
        "escalate_to_human"
    ) {

        return "escalated";
    }


    if (
        decision.action ===
        "stop"
    ) {

        return "stopped";
    }


    return "not_attempted";
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

    /*
       IMPORTANT:

       The API returns flat event summaries.
       Normalize them before the UI consumes them.
    */

    const events =
        (report.events || [])
            .map(normalizeEvent);


    setText(
        "activityCount",
        events.length
    );


    if (events.length === 0) {

        container.innerHTML = `
            <div class="empty-state">

                <div class="empty-icon">
                    ◇
                </div>

                <strong>
                    No payment events available
                </strong>

                <span>
                    Run the engine to populate activity.
                </span>

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
                        getEventStatus(
                            event
                        );


                    const recovered =
                        Number(
                            result.recovered_amount ||
                            0
                        );


                    return `

                        <button
                            type="button"
                            class="event-item event-row"
                            data-event-index="${index}"
                        >

                            <div class="event-main">

                                <div class="event-title-row">

                                    <div
                                        class="event-status-dot ${escapeHtml(
                                            status
                                        )}"
                                    ></div>


                                    <strong>

                                        ${escapeHtml(
                                            formatName(
                                                diagnosis.category ||
                                                "unknown"
                                            )
                                        )}

                                    </strong>


                                    <span
                                        class="event-status ${escapeHtml(
                                            status
                                        )}"
                                    >

                                        ${escapeHtml(
                                            formatName(
                                                status
                                            )
                                        )}

                                    </span>

                                </div>


                                <span>

                                    ${escapeHtml(
                                        formatName(
                                            event.payment_type ||
                                            "payment"
                                        )
                                    )}

                                    ·

                                    ${escapeHtml(
                                        event.event_id
                                    )}

                                </span>

                            </div>


                            <div class="event-amount">

                                <strong>

                                    ${
                                        recovered > 0
                                            ? formatCurrency(
                                                recovered
                                            )
                                            : formatCurrency(
                                                event.amount
                                            )
                                    }

                                </strong>


                                <span>

                                    ${escapeHtml(
                                        formatName(
                                            decision.action ||
                                            "no_action"
                                        )
                                    )}

                                </span>

                            </div>

                        </button>

                    `;
                }
            )
            .join("");


    container
        .querySelectorAll(
            ".event-row"
        )
        .forEach(element => {

            element.addEventListener(
                "click",
                () => {

                    const index =
                        Number(
                            element.dataset
                                .eventIndex
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
   AUDIT — SELECT EVENT
========================================================= */

async function selectEvent(
    element,
    event
) {

    document
        .querySelectorAll(
            ".event-row"
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
   AUDIT — LOADING
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

        <div class="audit-placeholder">

            <div class="audit-placeholder-icon">
                ↻
            </div>


            <span>
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
   AUDIT — ERROR
========================================================= */

function renderAuditError(
    message
) {

    const container =
        $("auditPanel");


    if (!container) {
        return;
    }


    container.innerHTML = `

        <div class="audit-placeholder">

            <div class="audit-placeholder-icon">
                !
            </div>


            <span>
                AUDIT ERROR
            </span>


            <h3>
                Unable to load audit trail
            </h3>


            <p>

                ${escapeHtml(
                    message
                )}

            </p>

        </div>

    `;
}


/* =========================================================
   AUDIT — TRACE
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


    if (
        entries.length ===
        0
    ) {

        container.innerHTML = `
            <div class="empty-state">
                No audit entries available.
            </div>
        `;

        return;
    }


    const diagnosisCategory =
        event.diagnosis?.category ||
        event.diagnosis ||
        "unknown";


    const decision =
        event.decision || {};


    const result =
        event.result || {};


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
                    Decision
                </span>

                <strong>

                    ${escapeHtml(
                        formatName(
                            decision.action ||
                            "unknown"
                        )
                    )}

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
                                entry.action ||
                                entry.event ||
                                entry.stage ||
                                stage;


                            return `

                                <div class="trace-event">

                                    <div class="trace-marker">

                                        <span>

                                            ${String(
                                                index + 1
                                            ).padStart(
                                                2,
                                                "0"
                                            )}

                                        </span>

                                    </div>


                                    <div class="trace-content">

                                        <span class="trace-stage">

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


        <div class="trace-final-result">

            <span>
                FINAL OUTCOME
            </span>


            <strong>

                ${escapeHtml(
                    formatName(
                        result.recovery_status ||
                        result.status ||
                        decision.action ||
                        "not_attempted"
                    )
                )}

            </strong>

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
        "COMPLETED",
    ];


    return (
        stages[index] ||
        "EVENT"
    );
}


function getEntryDetail(
    entry
) {

    const details =
        entry.details;


    if (!details) {

        return (
            entry.reasoning ||
            entry.message ||
            "Stage recorded in audit trail."
        );
    }


    if (
        typeof details ===
        "string"
    ) {

        return details;
    }


    if (
        details.reasoning
    ) {

        return details.reasoning;
    }


    if (
        details.reason
    ) {

        return `Decision reason: ${formatName(
            details.reason
        )}`;
    }


    if (
        details.action
    ) {

        return `Action: ${formatName(
            details.action
        )}`;
    }


    if (
        details.execution_result
    ) {

        return "Execution result recorded.";
    }


    return "Stage recorded in audit trail.";
}


function getEntryMetadata(
    entry
) {

    if (
        !entry.details ||
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

function updateDashboard(
    report
) {

    updateMetrics(
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


        setText(
            "baselineRecovered",
            formatCurrency(
                baseline.total_recovered
            )
        );


        setText(
            "baselineRecoveryRate",
            formatPercent(
                baseline.recovery_rate
            )
        );


        setText(
            "baselineUnsafeRetries",
            baseline.unsafe_retry_count ??
            baseline.unsafe_retries ??
            comparison.baseline_unsafe_retries ??
            0
        );


        setText(
            "reviveRecovered",
            formatCurrency(
                revive.total_recovered
            )
        );


        setText(
            "reviveRecoveryRate",
            formatPercent(
                revive.recovery_rate
            )
        );


        setText(
            "reviveUnsafeRetries",
            comparison.revive_unsafe_retries ??
            revive.unsafe_retry_count ??
            revive.unsafe_retries ??
            0
        );


        const unsafe =
            comparison.baseline_unsafe_retries ??
            baseline.unsafe_retry_count ??
            baseline.unsafe_retries ??
            0;


        setText(
            "comparisonInsight",
            `Revive prevented ${unsafe} unsafe retry actions while maintaining controlled recovery.`
        );


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


    openEngineModal();


    try {

        /*
           Start the REAL backend request
           immediately.

           The modal updates while the
           backend is processing.
        */

        const batchPromise =
            runRecoveryBatch();


        /* ---------------------------------------------
           INGESTION
        --------------------------------------------- */

        updateEngineStage(
            "ingestion"
        );


        await wait(
            450
        );


        /* ---------------------------------------------
           VALIDATION
        --------------------------------------------- */

        updateEngineStage(
            "validation"
        );


        await wait(
            550
        );


        /* ---------------------------------------------
           OPENROUTER AI
        --------------------------------------------- */

        updateEngineStage(
            "diagnosis"
        );


        await wait(
            650
        );


        /* ---------------------------------------------
           DETERMINISTIC POLICY
        --------------------------------------------- */

        updateEngineStage(
            "policy"
        );


        await wait(
            650
        );


        /* ---------------------------------------------
           EXECUTION
        --------------------------------------------- */

        updateEngineStage(
            "execution"
        );


        /*
           IMPORTANT:

           Do not declare success until
           the REAL backend response arrives.
        */

        const report =
            await batchPromise;


        /* ---------------------------------------------
           AUDIT
        --------------------------------------------- */

        updateEngineStage(
            "audit"
        );


        await wait(
            400
        );


        /* ---------------------------------------------
           COMPLETE
        --------------------------------------------- */

        completeEngineModal(
            report
        );


        /*
           Update live dashboard.
        */

        updateDashboard(
            report
        );


        /*
           Reload frozen experiment benchmark.
        */

        await loadExperimentComparison();


        showToast(
            "Recovery batch completed."
        );


    } catch (error) {

        console.error(
            "Recovery batch error:",
            error
        );


        failEngineModal(
            error
        );


        showToast(
            error.message ||
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
   MODAL CONTROLS
========================================================= */

function initializeEngineModal() {

    const closeButton =
        $("engineCloseBtn");


    const doneButton =
        $("engineDoneBtn");


    const backdrop =
        document.querySelector(
            ".engine-modal-backdrop"
        );


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            () => {

                /*
                   Do not allow closing while
                   the real batch is executing.
                */

                if (
                    !window.reviveBatchRunning
                ) {

                    closeEngineModal();

                }

            }
        );

    }


    if (doneButton) {

        doneButton.addEventListener(
            "click",
            () => {

                closeEngineModal();

                doneButton.textContent =
                    "Done";

            }
        );

    }


    if (backdrop) {

        backdrop.addEventListener(
            "click",
            () => {

                if (
                    !window.reviveBatchRunning
                ) {

                    closeEngineModal();

                }

            }
        );

    }
}


/* =========================================================
   UTILITY
========================================================= */

function wait(
    milliseconds
) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
            )
    );
}


/* =========================================================
   INITIALIZATION
========================================================= */

function initialize() {

    console.log(
        "REVIVE frontend initialized."
    );


    const runButtons = [
        $("runBatchBtn"),
        $("heroRunBtn"),
        $("finalRunBtn"),
        $("navRunBtn"),
    ];


    runButtons.forEach(
        button => {

            if (!button) {
                return;
            }


            button.addEventListener(
                "click",
                handleRunBatch
            );

        }
    );


    initializeEngineModal();

    initializeNavigation();


    /*
       Load the frozen Experiment 019
       benchmark immediately.
    */

    loadExperimentComparison();
}


/* =========================================================
   START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initialize
);