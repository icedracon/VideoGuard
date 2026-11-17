# Adaptive detective interview

Rank unresolved decisions by impact (0–3), uncertainty (0–3), and likely rework (0–3). The sum is a qualitative priority, not a calibrated probability. Ask about the highest priority item if it can affect a hard requirement, meaningful cost, or downstream feasibility. Prefer inspecting provided assets or checking available official model docs rather than questioning the user about observable facts.

Question template: one decision; why it matters in one sentence; 2–4 options including a recommended default; allow custom answer or “choose for me.” Avoid false choices. A user may answer multiple fields at once. Store answers in the brief and do not reask. After each answer update priorities. For high-risk work, summarize the contract before drafting or proposing spend. If a hard conflict persists, present alternatives and ask which constraint may change; never silently weaken it.

## Branches
- Goal unclear: purpose, audience, delivery channel, visual effect.
- Editing a real product/building/person: protected identity, geometry, text, colors, allowed edits, permitted assets. Do not promise pixel-exact preservation through generation.
- Image: intended composition, dimensions, typography, style and reference scope, delivery format. Ask only when relevant.
- Video: duration, target aspect, shot count, motion, camera, opening/ending state, continuity, audio/dialogue. If target model already fixed, verify only that model.
- Budget: maximum credits or dollars, known provider pricing, retries, whether cheap preview is appropriate.
- Repair: original brief, failed output, prompt and settings, observed defect, accepted assets. Ask for missing evidence, not an entire new brief.

## Stop criteria
No unresolved material blockers; remaining preferences are confirmed or delegated; acceptance criteria and budget status recorded. Unknown price or unsupported hard requirement blocks paid execution, not drafting. If user wants prompt only, provide conditional prompt and caveats without requiring optional details.
