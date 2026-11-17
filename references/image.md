# Still image creation and editing

Classify CREATE, EDIT, INPAINT, COMPOSITE, or UPSCALE. Identify actual model and host. Verify supported input images, mask/reference controls, output format, dimensions and paid pricing. In absence of verification mark unknown. Do not make up negative-prompt support, seeds, CFG, or 4K capability.

Preflight: intended subject and scene; spatial layout; composition/crop; aspect ratio; style and lighting; exact text and typography; reference quality; protected elements and allowed changes; rights/consent as appropriate. For editing, explicitly separate source of truth from style references. Prefer mask/local edit or deterministic postprocessing for strict preservation where practical. Upscaling cannot recover authentic detail not present. For exact typography, logo or product details, consider compositing verified assets after generation rather than trusting synthesis.

Prompt scaffold: task and subject; scene/composition; lighting/material and visual intent; required details; preservation and allowed edits; verified settings separately. Do not add generic adjectives that compete with core constraints. For a reference-based edit describe the delta and list protected elements. If image will feed video, inspect framing, placement, visible joints/props, movement space and visual continuity.

Acceptance: compare original and result; check protected region, text, logos, composition, color, intended edit and actual delivered pixel dimensions. Use crop comparisons or deterministic utilities when available. Mark visual inspection UNKNOWN if no asset accessible. Do not claim geometric equivalence from appearance alone. Suggest a minimal repair and avoid recreating accepted areas.

Official guidance starting points (verify current model/host): https://platform.openai.com/docs/guides/image-generation ; https://ai.google.dev/gemini-api/docs/image-generation .
