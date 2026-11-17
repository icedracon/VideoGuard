# Cost planning

Separate dollars, provider credits, and LLM tokens. Never total different units or infer conversion. Collect actual price per attempt and billing rounding/failed-job policy from current provider quote or user. Include previews, final renders, reserved retries, editing and optional reviews. Unknown prices remain unknown. Treat subscriptions as distinct from marginal consumption.

Planned = sum(quantity × price) for base steps. Reserved = sum(quantity × price) for retry steps. Authorized worst case = planned + reserved (plus known fees). Compare against cap in same unit. Unknown price means budget certification unavailable, even if known subtotal is under cap. If known subtotal exceeds cap, block regardless of unknowns. Propose a smaller scope or alternate verified option, not silent quality reduction.

Choose models by hard constraints first, then plausible total cost of accepted outputs. A cheaper attempt is not always a cheaper accepted result. Do not invent success rates. If empirical acceptance rates exist for comparable tasks, label sample size and use them cautiously. Compare preview overhead against plausible avoided repeats; do not automatically generate previews. Reuse approved assets, do local transformations where sufficient, avoid repeated model debate and retain only relevant context.

Optional deterministic calculator: `python scripts/budget.py plan.json` (Python standard library only). See `tests/budget-example.json`. This checks arithmetic, not actual provider prices or execution. No network or paid generation.
