# Production workflow and budget

For each shot keep: ID, purpose, duration, approved reference asset, target model/version and mode, prompt, acceptance criteria, cost ceiling, actual charge, attempt count, status and failure notes. For dependencies record which shots rely on a shared reference. If changing a shared asset, review affected shots before deciding which need reruns.

## Cost math
When all rates are known, planned costs = sum of planned attempts times the corresponding per-attempt charge + preview/postproduction costs. Worst-case authorized cost = sum of maximum authorized attempts times their charges + other known costs. If per-second pricing is used, compute per-attempt charge from the actual selected duration and resolution. If any rates are missing, label totals partial. For monthly plans, keep subscription overhead separate from marginal credits and do not present sunk cost as refundable.

Observed cost per accepted shot = total generation spend across all attempts / accepted shots (undefined when none accepted). Compare the same scope, quality target and billing unit. To choose between model A and B using empirical data, compare their measured acceptance rates and costs from comparable shots; don't invent rates.

## Example (illustrative credits only)
Four shots, each costs 20 credits per attempt; one retry per shot allowed. Base generation cost = 80 credits, maximum = 160 credits. A separate preview step costing 8 credits increases both totals if used once. Under a 100-credit cap, the full retry allowance is not affordable: allocate remaining credits only to failed shots within the cap, or adjust the plan with user approval.

## Handoff checklist
- Script → storyboard: each shot has a clear action and enough screen time.
- Storyboard → still: reference frames show what needs to move; framing matches delivery format; identities and products are approved.
- Still → video: selected model accepts input; motion fits frame and duration; user approves spend.
- Video → edit: important continuity, action, framing and timing checked; audio verified if required and available.
- Edit → delivery: inspect final result against original brief, not just the latest prompt.
