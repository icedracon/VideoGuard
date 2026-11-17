# Cross-model compiler and approval gates

For each stage define ID, upstream version IDs, artifact type, intended downstream model/host, required inputs, allowed changes, acceptance tests, cost, and status (DRAFT/REVIEW/APPROVED/BLOCKED). Keep assets distinct from instructions. Never describe an unexecuted stage as complete.

Typical pipeline: brief → script → shot plan → approved keyframes → video preflight → clips → edit → final acceptance. Use the simplest adequate workflow; no extra AI reviewers without benefit. Verify target model's actual input schema and limits; reject mismatched aspect ratio, absent reference, unsupported audio/control, discontinuity, missing ending state or stale asset version. An optional independent review can challenge high-cost stages; one model reviewing its own work is not independent. Use deterministic checks first where possible.

If a downstream failure occurs, record observable defect, evidence, possible upstream cause, confidence (low/medium/high), alternative causes and cheapest diagnostic. Invalidate only affected dependency descendants, retaining approved unrelated assets. Change one variable where practical. Do not assign blame to a provider without evidence. Stop repeated failures and propose a different route.

Approval: user confirms brief/keyframes before expensive or irreversible stages; confirm exact scoped paid action separately. This skill does not contain provider integrations or intercept third-party UI. If no tool exists, deliver copy-ready handoff packages for manual execution.
