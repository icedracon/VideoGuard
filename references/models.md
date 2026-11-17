# Model and platform guidance

Reference snapshot: 2026-11-17. Models, pricing and supported controls change; check official docs for the specific host, endpoint, version and subscription before recommending exact settings. The notes are practical heuristics, not an exhaustive capability registry.

## Runway
- Image-to-video: describe animation and camera movement primarily; inspect the input image for visual cues that conflict with motion. A prompt cannot reliably enforce exact preservation of hidden geometry.
- Text-to-video: specify the visible scene, subject and action, then motion/camera. Start with key details and add specificity where needed.
- Prefer positive visual descriptions rather than blanket prohibitions where the model guidance recommends it.
Official sources:
- https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide
- https://help.runwayml.com/hc/en-us/articles/42460036199443-Text-to-Video-Prompting-Guide
- https://help.runwayml.com/hc/en-us/articles/46182941379347-Introduction-to-Prompting

## Higgsfield and hosted models (Kling, Seedance, Veo, Wan, etc.)
- Higgsfield is a host for multiple video model families and has additional tools. Determine the actual selected model and mode; settings differ by family and version.
- Check available image/reference/video inputs, start/end frames, duration, resolution, aspect ratio and model-specific controls. Do not assume the same feature is exposed by all hosts.
- Use a model-specific camera preset if it is available and suits the shot; avoid contradictory prompt instructions.
Official sources:
- https://higgsfield.ai/ai-video
- https://higgsfield.ai/blog/photo-to-ai-video
- https://open.higgsfield.ai/models/kling-video/v4.0/image-to-video/api-reference

## Veo (Google)
- Use concrete descriptions of the subject, action, scene and camera. For image-to-video, emphasize desired movement; ensure the first frame supports the planned action.
- Verify availability of audio, negative prompt fields, reference frames and other controls for the specific model/surface, not merely the model family.
Official sources:
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice

## Other providers
Use the same preflight rubric. Read the current official prompting and parameter guide if available. If browsing is unavailable, provide general guidance and identify unsupported or unconfirmed settings instead of guessing. Never equate a subscription's web credits with API pricing.
