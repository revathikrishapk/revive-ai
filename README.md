# Revive AI
**Track 03 — AI Revenue Recovery | Razorpay AI Buildathon 2026**

Revive AI recovers failed revenue by combining AI failure diagnosis
with deterministic guardrails that decide when to retry, when to stop,
and when to escalate — with every decision auditable and every outcome
 measurable.

---

## The Problem

When a payment fails, blindly retrying everything wastes money,
repeatedly inconveniences customers, and mishandles risky cases like
fraud holds. Revive separates diagnosis from decision-making:

> **AI diagnoses the failure. Deterministic policy decides whether
> recovery is allowed.**

This design prevents the language model from directly authorizing any
payment action.

## Results (500-event synthetic batch)

| Metric | Value |
|---|---:|
| Events processed | 500 |
| Total revenue at risk | ₹19,87,156.17 |
| Gross revenue recovered | ₹6,40,757.39 |
| Retry cost | ₹582.00 |
| Net revenue recovered | ₹6,40,175.39 |
| Gross recovery rate | 32.24% |
| Recovery attempts made | 291 / 500 |
| Successful recoveries | 158 |
| Attempt success rate | 54.30% |
| Human escalations | 91 (18.20%) |
| **Revenue protected by guardrails** | **₹7,93,054.49** |

Full per-event audit trail available via `GET /audit-log/{event_id}`.

### AI diagnosis performance

| Metric | Value |
|---|---:|
| Total events | 500 |
| Correct diagnoses | 482 |
| Diagnosis accuracy | 96.79% |
| Fallback diagnoses | 2 (0.40%) |
| Validation failures (caught, not silent) | 9 |
| Provider failures | 0 |
| API calls made | 29 |
| Cache hits | 478 |

Only 29 live API calls were needed to diagnose 500 events — 478 were
served from a diagnosis cache, which matters as much as the accuracy
number: this isn't a system that blindly calls an LLM per event.

## Why Revive Stopped or Escalated Instead of Retrying Everything

| Decision reason | Count |
|---|---:|
| Safe to retry | 291 |
| Fraud hold | 90 |
| Retry cap reached | 117 |
| Low confidence | 1 |
| Economic floor | 1 |

Revive automatically retried only 291 of 500 events. The remaining 209
were deliberately withheld from automated action — 90 fraud-flagged
cases and 117 retry-cap violations never reached auto-retry, and one
low-confidence diagnosis and one sub-₹100 transaction were correctly
blocked by policy.

## Revive vs. Naive Retry-Everything (Controlled Experiment)

Same 500 synthetic events, two strategies, run head-to-head:

| Metric | Naive Retry | Revive |
|---|---:|---:|
| Attempts | 500 | 291 |
| Gross recovered | ₹8,44,938.34 | ₹6,40,757.39 |
| Recovery rate | 42.52% | 32.24% |
| Fraud-hold retries | 113 | **0** |
| Retry-cap violations | 118 | **0** |
| Economic-floor violations | 1 | **0** |

**This is the central thesis of the product.** Naive retry-everything
recovers more raw revenue in this batch — but at the cost of retrying
113 fraud-held transactions, violating retry caps 118 times, and
ignoring the economic floor once. Revive deliberately trades some gross
recovery for zero policy violations. That trade-off, made explicit and
measured rather than assumed, is the product.

## Recovery Performance by Failure Category

| Failure Type | Events | At Risk | Recovered | Recovery Rate |
|---|---:|---:|---:|---:|
| Network error | 115 | ₹4,66,745.37 | ₹3,10,004.82 | **66.42%** |
| Mandate failure | 61 | ₹1,53,785.12 | ₹68,351.41 | 44.45% |
| Insufficient funds | 116 | ₹5,09,731.55 | ₹1,50,678.78 | 29.56% |
| Expired card | 93 | ₹3,84,878.35 | ₹1,11,722.38 | 29.03% |
| Fraud hold | 113 | ₹4,57,926.05 | ₹0 | 0% (never auto-retried, by design) |

Network errors recover best (66.42%) because they're genuinely transient.
Fraud holds recover 0% by design — they're routed to human escalation,
not attempted, which is the correct and safe behavior.

## Recovery Performance by Payment Type

| | One-off | Subscription |
|---|---:|---:|
| Events | 258 | 242 |
| At risk | ₹13,34,921.14 | ₹6,52,235.03 |
| Net recovered | ₹4,02,193.47 | ₹2,37,981.92 |
| Net recovery rate | 30.13% | 36.49% |

Subscription failures recover at a meaningfully higher rate than
one-off payments — the category-aware retry cadence (below) accounts
for this difference rather than treating all failures identically.

## Architecture

```
Failed Payment Event
        ↓
Validation / Schema
        ↓
AI Diagnosis (OpenRouter-compatible client)
        ↓
Deterministic Policy Engine
   ┌─────────────┬──────────────────┬──────────┐
   │ Retry       │ Escalate to Human│ Stop     │
   └─────────────┴──────────────────┴──────────┘
        ↓
Mock Executor + Idempotency Guard
        ↓
Audit Logging + Reporting
```

The AI layer has one job: propose a failure category (`network_error`,
`insufficient_funds`, `expired_card`, `fraud_hold`, `mandate_failure`,
`unknown`), a confidence score, and a short explanation. **It cannot
decide to retry, stop, escalate, or execute anything.** That authority
belongs entirely to the deterministic Policy Engine.

## Guardrails

| Guardrail | Rule |
|---|---|
| Economic floor | Payments under ₹100 are stopped |
| Retry cap | 3+ previous retries → stopped |
| Fraud protection | `fraud_hold` is never auto-retried — always escalated |
| Confidence protection | Confidence below 0.55 → escalated, never auto-actioned |

## Category-Aware Retry Cadence

Retry timing isn't uniform — it's chosen per failure type and payment type:

| Failure type | One-off | Subscription |
|---|---|---|
| Network error | Immediate | 24h, then 72h |
| Insufficient funds | 24h | 24h, then 72h |
| Expired card | 72h | 24h, then 72h |
| Mandate failure | — | 24h, then 72h |
| Unknown | Never auto-retried — escalated | Never auto-retried — escalated |

## What Broke, and How I Fixed It

Across the 500-event batch, the AI diagnosis layer produced **9
validation failures** — cases where the model's output didn't conform
to the required structured schema. Rather than letting a malformed
response silently reach the policy engine, every diagnosis is validated
before use; a validation failure triggers a safe fallback to an
`unknown` diagnosis with zero confidence, which the policy engine always
routes to human escalation — never a guess. Two events fell all the way
through to this fallback path (a 0.40% fallback rate), and in every
case the system degraded safely rather than crashing or silently
approving an unsafe retry. Provider-level failures were 0/500 in this
batch, but the fallback path exists specifically for that scenario too.

The idempotency guard on the executor was built for the same reason:
a duplicate event delivery (e.g. a repeated webhook) must never result
in a transaction being actioned twice. This is enforced with an
event-ID-based check before any simulated execution occurs.

## Running It

```
GET /                          # dashboard UI
GET /health                    # health check
POST /run-batch                # run a recovery batch
GET /audit-log/{event_id}      # per-event audit trail
GET /experiment/latest         # latest experiment result (baseline vs. Revive)
```

## What Revive Is Not Yet

This is a simulation/prototype. It does not connect to a real payment
gateway, does not move real money, and the `RecoveryExecutor` is
explicitly a mock. Real payment execution, live notification channels,
and production merchant data are future integration work, not part of
the current implementation.

## Stack

OpenRouter-compatible OpenAI client for diagnosis, deterministic Python
policy engine, mock execution layer with idempotency guarding,
append-only JSONL audit logging.
