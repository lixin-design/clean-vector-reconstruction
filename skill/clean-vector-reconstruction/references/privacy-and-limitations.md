# Privacy and Limitations

Use this reference when content may be private, publication is requested, permissions are unclear, or the input may be outside validated scope.

## Permission gate

Before reading or transforming material, confirm:

- the user authorized access to the exact reference and related files;
- ownership/licensing permits the requested local use;
- publication permission is separate from local-processing permission;
- the output directory is authorized;
- no excluded directory or case must be inspected;
- no installation or external access is required without approval.

Stop when the reference or permission is missing. Do not inspect adjacent private directories to fill gaps.

## Private-material boundary

Keep private materials out of reusable skills, public examples, and release folders. Do not copy or summarize:

- private reference images or screenshots;
- private SVG or source files;
- artwork-specific prompts and reports;
- competition/submission information;
- identifying object descriptions;
- private absolute paths;
- diagnostic images that reveal the private work.

Convert only permitted evidence into abstract rules such as primary subject, base blocks, repeated elements, gradients, shared boundaries, key landmarks, and validation gates.

When reference publication permission is uncertain, public-facing completeness summaries must use generic object-family terms. Do not expose identifying nouns, private labels, or artwork-specific inventory names; retain detailed case-authored inventories only inside their authorized private workspace.

## Public examples

Publish an example only when rights and intended publication are explicit. Recheck references, previews, overlays, difference images, reports, metadata, scripts, and paths because any of them may disclose protected content.

Generated Markdown and JSON reports can leak usernames, user-specific local folders or absolute local paths, executable paths, and private directory names when absolute paths are recorded. Use each script's `--path-mode relative` or `--path-mode basename` for material that may be shared. Use `absolute` only for explicitly private debugging, and inspect the rendered report before committing it to GitHub or another public location. Path-display settings affect reporting only; scripts may still use real paths internally.

Treat GitHub publication as a separate authorized task. Do not create release files during reconstruction, protocol revision, or Skill drafting unless explicitly requested.

Local region crops, preview crops, overlays, difference crops, region summaries, and other diagnostic images inherit the reference image's privacy and publication status. Local processing permission does not grant permission to publish them. Do not place them in reusable or public locations without explicit publication permission.

## Supported scope

The validated primary scope is:

- flat and semi-flat raster illustration;
- geometric color-block illustration;
- clear semantic regions;
- solid fills, simple curves, repeated elements, and limited gradients;
- editable SVG intended for Adobe Illustrator.

Do not use the Skill for photography, watercolor, oil painting, dense natural texture, highly realistic lighting, a missing/unclear reference, or automatic pixel-perfect conversion that ignores editability.

## Experimental areas

`line-art`, `logo`, and `high-fidelity` remain experimental. Position tolerance varies by canvas size and design importance. Complexity limits are warnings, not universal hard caps. SVG rendering and Illustrator behavior may vary by version and renderer.

## Claims not allowed

Do not claim:

- support for every image type;
- pixel-perfect conversion with low complexity;
- production readiness without real human review;
- Illustrator compatibility that was not actually tested;
- editable gradients or easy anchor editing without reviewer evidence;
- successful reconstruction solely from rendering or numerical metrics;
- permission to publish based only on permission to process locally.

State unresolved limitations plainly and narrow or stop the task when necessary.
