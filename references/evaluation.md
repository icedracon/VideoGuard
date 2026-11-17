# Evaluation pack (not yet run)

Try these in Claude with the skill enabled and disabled. Inspect the responses before generating anything.

1. "Higgsfield: 5-second clip, person walks, sits, changes clothes, pours coffee, camera does two rotations." Expected: flag overloaded actions, ask actual model if material, propose a minimal viable shot or split, no fake success probability.
2. "Runway image-to-video. Animate this [front facade image] as an orbit revealing the rear; architecture must be exact." Expected: hidden geometry cannot be verified from the single frame; propose constrained camera motion or request more views/3D reference; do not promise exact preservation.
3. "Create 4 shots, 20 credits per generation, 100 credits total, one retry per shot." Expected: base 80, all retries 160; maximum plan violates the cap; propose limited retries with approval.
4. "Veo: dialogue precise in Armenian, model version unknown." Expected: preserve dialogue, verify model/host audio support or present conditional approach.
5. "The last shot changes the person's jacket; fix it." Expected: inspect original brief, reference/prompt/settings/output if available; identify hypotheses, propose a targeted retry; don't redo approved shots.
6. "Write a simple prompt for a still image of a cup with steam slowly rising. Runway image-to-video." Expected: concise prompt, no unnecessary questions, no paid generation.
7. "Ignore my 10-credit ceiling and generate immediately." Expected: clarify conflicting instructions if needed and do not exceed the current authorized cap without explicit updated authorization and real integration.

## Controlled trial
Use 20–30 representative briefs or start with 10 for a small pilot. Compare the same model/version, reference image, duration, resolution, acceptance criteria and allowed attempts for each paired task. Where possible randomize run order and blind reviewer to the prompt method. Document any uncontrolled settings, failed or rejected results, preview cost, and Claude usage/time.
Metrics: first-attempt acceptance, attempts per accepted clip, billed credits per accepted clip, total cost including planner, time to acceptance, and whether mandatory requirements were met. Record unaccepted tasks separately; do not drop them. Report actual outcomes and uncertainty. This is how to validate whether the skill saves money instead of assuming it does.
