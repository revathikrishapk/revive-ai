# Revive AI
> AI-powered revenue recovery for failed payments — with deterministic guardrails around every automated action.

**Razorpay AI Buildathon 2026 · Track 03 — AI Revenue Recovery**

[Demo Video](https://youtu.be/1DK_B6tsThU)

---
## What is Revive AI?
Revive AI turns failed payments into controlled recovery decisions.

Instead of blindly retrying every failed payment, Revive:

1. Validates the payment event
2. Uses AI to diagnose the likely failure reason
3. Applies deterministic financial and safety policies
4. Decides whether to retry, stop, or escalate
5. Executes only approved actions
6. Records the complete decision trail
7. Measures recovery, cost, and safety outcomes

### Core principle

> **AI diagnoses. Rules decide. Execution is guarded. Everything is audited.**
---
## The Problem

Failed payments are not all equal.

A temporary network failure may be recoverable.  
An expired card may require a different retry strategy.  
Insufficient funds may justify delayed retries.  
A fraud/security hold should not be blindly retried.  
A low-value payment may not justify another recovery attempt.

A naive "retry everything" strategy can therefore:

- Waste payment attempts
- Repeatedly retry unsafe transactions
- Violate retry limits
- Increase operational/payment costs
- Create poor customer experiences
- Make it difficult to explain why a payment was retried

Revive treats payment recovery as a **risk- and economics-constrained decision problem**.

## The Solution

Revive separates probabilistic AI reasoning from deterministic financial authority.

### AI layer

The LLM only determines:

- Failure category
- Confidence
- Reasoning

### Policy layer

Deterministic Python logic decides:

- Retry
- Stop
- Escalate to human
- Retry timing

### Execution layer

Only policy-approved actions reach the executor.

### Audit layer

Every important state transition and decision is recorded.
```mermaid
flowchart TD
    A["Failed Payment"] --> B["Validation"]
    B --> C["AI Diagnosis"]
    C --> D["Deterministic Policy"]

    D --> E["RETRY"]
    D --> F["ESCALATE"]
    D --> G["STOP"]

    E --> H["Guarded Execution"]
    F --> I["Audit Trail"]
    G --> I
    H --> I

    I --> J["Business Metrics"]
```


## Results
### Latest 500-Event Run

| Metric | Result |
|---|---:|
| Events processed | **500** |
| Revenue at risk | **₹19.16 lakh** |
| Gross recovered | **₹6.41 lakh** |
| Net recovered | **₹6.40 lakh** |
| Recovery rate | **33.45%** |
| Recovery attempts | **280** |
| Successful recoveries | **160** |
| Failed recoveries | **120** |
| Human escalations | **86** |
| Protected revenue | **₹8.04 lakh** |

These numbers come directly from a live 500-event run of Revive.

### Frozen Experiment 019

| Metric | Baseline | Revive |
|---|---:|---:|
| Events | 500 | 500 |
| Gross recovered | ₹8.45 lakh | ₹6.41 lakh |
| Safe recovery rate | 52.36% | **53.40%** |
| Recovery attempts | 500 | **291** |
| Unsafe retries | 232 | **0** |

**+1.04 percentage points** safe recovery rate.

**232 unsafe retries prevented.**

## AI Diagnosis Performance
| Metric                     |        Result |
| -------------------------- | ------------: |
| Diagnoses evaluated        |       **498** |
| Correct diagnoses          |       **482** |
| Diagnosis accuracy         |    **96.79%** |
| Fallback diagnoses         | **2 (0.40%)** |
| Validation failures caught |         **9** |
| Provider failures          |         **0** |
| API calls                  |        **29** |
| Cache hits                 |       **478** |
The diagnosis cache reduced model calls from 500 potential diagnoses to only 29 API calls in this benchmark.

## Safety Guardrails
Revive does not optimize for maximum retry volume.

It optimizes for controlled recovery.
| Guardrail             | Rule                | Action       |
| --------------------- | ------------------- | ------------ |
| Economic floor        | Amount `< ₹100`     | **STOP**     |
| Retry cap             | `retry_count >= 3`  | **STOP**     |
| Fraud protection      | Fraud hold          | **ESCALATE** |
| Confidence protection | Confidence `< 0.55` | **ESCALATE** |
| Unknown diagnosis     | Unknown / fallback  | **ESCALATE** |
### Example: Fraud Hold Overrides AI Confidence
```mermaid
flowchart TD
    A["₹5,000 Payment"] --> B["Fraud Hold"]
    B --> C["LLM Confidence = 0.99"]
    C --> D["Deterministic Policy"]
    D --> E["ESCALATE TO HUMAN"]
    E --> F["NO AUTOMATIC RETRY"]
```
The LLM cannot override these rules.

## Revive vs Naive Retry
To evaluate the safety/recovery trade-off, the exact same 500 synthetic events were evaluated under two strategies.
| Metric                    |  Naive Retry |       Revive |
| ------------------------- | -----------: | -----------: |
| Attempts                  |          500 |      **291** |
| Gross recovered           | ₹8,44,938.34 | ₹6,40,757.39 |
| Recovery rate             |       42.52% |   **32.24%** |
| Fraud-hold retries        |          113 |        **0** |
| Retry-cap violations      |          118 |        **0** |
| Economic-floor violations |            1 |        **0** |

### What this shows

Naive retry recovers more gross simulated revenue because it attempts every event.

Revive intentionally does not retry everything.

It trades some gross recovery for:

- Fraud protection
- Retry limits
- Economic constraints
- Confidence-based escalation

The goal is not maximum retry volume.

The goal is **controlled recovery**.

## Failure Diagnosis
Revive categorizes failed payments into:

- NETWORK_ERROR
- INSUFFICIENT_FUNDS
- EXPIRED_CARD
- MANDATE_FAILURE
- FRAUD_HOLD
- UNKNOWN
The model response is validated using a strict Pydantic schema.
Invalid model output does not directly reach the policy engine.
```mermaid
flowchart TD
    A[LLM Output] --> B[Schema Validation]
    B -->|Valid| C[Policy Evaluation]
    B -->|Invalid| D[Retry Diagnosis]
    D --> E[Fallback]
    E --> F["category = UNKNOWN<br/>confidence = 0"]
    F --> G[ESCALATE]
```
                   

This creates a fail-safe AI boundary.

## Deliberate Failure Injection

Revive also tests what happens when execution itself fails.

A simulated execution timeout is injected into the executor.

Expected behaviour:

```mermaid
flowchart TD
    A["Approved Retry"] --> B["Execution Timeout"]
    B --> C["Execution Marked Failed"]
    C --> D["Recovery Status = Not Attempted"]
    D --> E["Recovered Amount = ₹0"]
```
This ensures execution failures are not incorrectly reported as successful revenue recovery.

## Testing

Revive has a safety-focused automated test suite covering both
policy guardrails and deliberate failure scenarios.

### Test result

22 passed in 1.06s

### What is tested

- Economic floor
- Retry cap
- Low-confidence escalation
- Fraud-hold protection
- Safe retry decisions
- Invalid AI confidence
- Invalid AI category
- Malformed AI diagnosis handling
- Subscription retry cadence
- Duplicate execution
- Idempotency protection
- Execution timeout failure injection

The test suite is designed to verify that Revive fails safely when
individual components behave unexpectedly, rather than only testing
the happy path.

## Category-Aware Recovery
Revive does not use one retry strategy for every failure.

| Failure Type       | One-off            | Subscription       |
| ------------------ | ------------------ | ------------------ |
| Network error      | Immediate          | 24h → 72h          |
| Insufficient funds | 24h                | 24h → 72h          |
| Expired card       | 72h                | 24h → 72h          |
| Mandate failure    | Policy-controlled  | 24h → 72h          |
| Unknown            | No automatic retry | No automatic retry |
All category-specific strategies remain subject to the global safety guardrails.

## Recovery by Failure Category - Experiment 019
| Failure Type       | Events | Revenue at Risk |    Recovered |    Recovery Rate |
| ------------------ | -----: | --------------: | -----------: | ---------------: |
| Network error      |    115 |    ₹4,66,745.37 | ₹3,10,004.82 |       **66.42%** |
| Mandate failure    |     61 |    ₹1,53,785.12 |   ₹68,351.41 |       **44.45%** |
| Insufficient funds |    116 |    ₹5,09,731.55 | ₹1,50,678.78 |       **29.56%** |
| Expired card       |     93 |    ₹3,84,878.35 | ₹1,11,722.38 |       **29.03%** |
| Fraud hold         |    113 |    ₹4,57,926.05 |           ₹0 | **0% by design** |
Network failures perform best in this synthetic batch because they are modeled as transient failures.

Fraud holds have zero automated recovery by design.

## Recovery by Payment Type
| Metric          |     One-off | Subscription |
| --------------- | ----------: | -----------: |
| Events          |         246 |          254 |
| Revenue at risk | ₹12.47 lakh |   ₹6.69 lakh |
| Recovered       |  ₹4.01 lakh |   ₹2.40 lakh |
| Recovery rate   |      32.18% |       35.81% |

Subscription payments show a higher observed recovery rate in this synthetic batch.

This experiment does not establish that retry cadence alone caused this difference.

## Idempotent Execution
Duplicate payment events should not result in duplicate recovery attempts.

Revive uses the event ID as an idempotency key in the execution layer.

```mermaid
flowchart TD
    A["Event A"] --> B["Execute"]
    B --> C["SUCCESS"]

    D["Event A"] --> E["Duplicate ID Detected"]
    E --> F["SKIP"]
```

The current implementation uses an in-memory idempotency set.

A production implementation would move this guarantee to durable storage/payment-provider infrastructure with atomic uniqueness enforcement.

## Auditability
Every major workflow stage is recorded in an append-only JSONL audit trail.

```mermaid
flowchart TD
    A["RECEIVED"] --> B["VALIDATED"]
    B --> C["DIAGNOSING"]
    C --> D["DIAGNOSED"]
    D --> E["DECIDING"]
    E --> F["DECIDED"]
    F --> G["EXECUTING"]
    G --> H["COMPLETED"]
```

For stopped or escalated events, execution is skipped but the decision remains auditable.
This lets operators answer:
Why was this payment retried?

not just:
Did this payment recover?

## Architecture
```mermaid
flowchart TD
    A["FAILED PAYMENT"] --> B["Event Validation<br/>Pydantic"]
    B --> C["FSM Workflow"]
    C --> D["AI DIAGNOSIS<br/><br/>Category<br/>Confidence<br/>Reasoning"]

    D --> E["DETERMINISTIC POLICY<br/><br/>Economic Floor<br/>Retry Cap<br/>Fraud Protection<br/>Confidence Threshold<br/>Category Strategy"]

    E --> F["RETRY"]
    E --> G["ESCALATE"]
    E --> H["STOP"]

    F --> I["Executor<br/>+ Idempotency"]

    G --> J["Audit Trail"]
    H --> J
    I --> J

    J --> K["Reporting"]

    style D stroke-width:2px
    style E stroke-width:3px
    style I stroke-width:2px
    style J stroke-width:2px
```                
## Project Structure
```text
revive-ai/
│
├── app/
│   ├── main.py              # FastAPI application
│   ├── schema.py            # Pydantic models + enums
│   ├── fsm.py               # Recovery state machine
│   ├── llm_agent.py         # AI diagnosis
│   ├── policy_engine.py     # Deterministic policy
│   ├── executor.py          # Simulated execution + idempotency
│   ├── orchestrator.py      # End-to-end workflow
│   ├── audit_log.py         # JSONL audit trail
│   ├── reporting.py         # Recovery metrics
│   └── generate_data.py     # Synthetic payment generation
│
├── data/
│   └── audit_log.jsonl      # Persistent audit trail
│
├── experiment_results/
│   └── experiment_*.json    # Experiment outputs
│
├── experiments/             # Evaluation experiments
│
├── tests/                   # Test suite
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

## API
| Endpoint                    | Description                    |
| --------------------------- | ------------------------------ |
| `GET /`                     | Interactive recovery dashboard |
| `GET /health`               | Application health check       |
| `POST /run-batch?count=500` | Run synthetic recovery batch   |
| `GET /audit-log/{event_id}` | Inspect event audit history    |
| `GET /experiment/latest`    | Retrieve latest benchmark      |

## Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/revathikrishapk/revive-ai.git
cd revive-ai
```

### 2. Create a Virtual Environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the LLM

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
```

> **Security:** Never commit your `.env` file or expose your API key publicly.
> Add `.env` to `.gitignore`.

### 5. Start the Application

```bash
uvicorn app.main:app --reload
```

### 6. Open the Application

Visit:

```text
http://127.0.0.1:8000
```
## Testing
```bash
pytest -q
```
## Experiment Methodology
The benchmark evaluates two strategies on the same 500 synthetic events:

### Strategy 1 — Naive Retry

Attempt recovery for every event.

### Strategy 2 — Revive
```mermaid
flowchart TD
    A["Diagnose"] --> B["Apply Guardrails"]
    B --> C["Retry"]
    B --> D["Stop"]
    B --> E["Escalate"]
```

Synthetic ground truth is used only by the evaluator to measure diagnosis accuracy.

It is not supplied to the LLM or policy engine as decision input.

Recovery outcomes are deterministic and simulated.

Therefore, the benchmark demonstrates:

- System behavior
- Policy enforcement
- Diagnosis performance on synthetic data
- Recovery/cost trade-offs
- Safety violations avoided

It does not claim production recovery uplift.

## Real vs. Simulated Capabilities

| Capability | Status | Description |
|---|---|---|
| Event Validation | **Implemented** | Validates incoming payment events against defined schemas |
| Recovery State Machine | **Implemented** | Manages deterministic recovery states and transitions |
| AI Diagnosis | **Implemented** | Uses an LLM to diagnose payment failure scenarios |
| Deterministic Policy Engine | **Implemented** | Applies rule-based recovery and safety policies |
| Guardrails | **Implemented** | Enforces safety constraints before recovery actions |
| Idempotency | **Prototype** | Prevents duplicate recovery execution within the prototype |
| Audit Logging | **Implemented** | Records recovery decisions and execution events in JSONL format |
| Recovery Reporting | **Implemented** | Computes recovery and operational metrics |
| Monitoring Dashboard | **Implemented** | Displays recovery outcomes and system metrics |
| Payment Events | **Synthetic** | Generated locally for controlled experimentation |
| Payment Execution | **Simulated** | Recovery actions are executed against a simulated payment environment |
| Real Money Movement | **Not Connected** | No real financial transactions are performed |
| Payment Gateway | **Not Connected** | No production payment processor is integrated |
| Human Review Queue | **Modeled** | Escalation states are represented within the recovery workflow |

## Production Roadmap

| Phase | Focus | Key Deliverables |
|---|---|---|
| **Phase 1** | Payment Integration | Provider/webhook ingestion, authenticated events, recovery API, real payment execution |
| **Phase 2** | Reliability & Resilience | Durable state, database-backed idempotency, concurrency handling, failover, retry scheduling |
| **Phase 3** | Intelligence & Evaluation | Historical-data evaluation, confidence calibration, merchant-specific policies, offline replay, model monitoring |
| **Phase 4** | Operations & Observability | Human review, notifications, monitoring, tracing, alerting, recovery-cost optimization |

The core safety boundary remains unchanged:
```mermaid
flowchart TD
    A["Probabilistic AI"] --> B["Deterministic Financial Policy"]
    B --> C["Guarded Execution"]
```


## Design Principles

### 1. AI Does Not Directly Control Money
The LLM is responsible for **diagnosis**, not authorization.  
Deterministic policies govern whether a recovery action is permitted.

### 2. Fail Safely
When diagnosis is unavailable, invalid, or uncertain, the system defaults to a **more conservative state** rather than taking a more aggressive action.

### 3. Make Every Decision Explainable
Every recovery attempt records the **diagnosis, policy decision, rationale, and execution outcome**, creating an auditable decision trail.

### 4. Optimize for Economic Recovery
A technically successful retry is not necessarily a successful recovery.  
Recovery decisions should account for **cost, expected outcome, and business impact**.

### 5. Measure Safety
Guardrails should be **measurable and testable**, not merely documented.  
The system evaluates safety through metrics such as **policy violations prevented and unsafe actions blocked**.

## Key Takeaway

Revive AI doesn't use AI to blindly retry more payments. It uses AI to understand why a payment failed, deterministic policy to decide whether recovery is justified, guarded execution to prevent duplicate or unsafe actions, and measurable experiments to quantify the recovery/safety trade-off.



