# 0003. Permissive licences only

- Status: Accepted
- Date: 2026-10-14

## Context

The repository is published under Apache-2.0 so that anyone can use it, including in a product.
The first perception prototype used Ultralytics YOLO, which is AGPL-3.0: shipping it inside the
robot would oblige the whole stack to be released under the AGPL. Several open models are also
published under non-commercial licences, which would make the same problem worse.

## Decision

Code dependencies and model weights must be Apache-2.0, MIT or BSD, checked on the model card
before adoption and pinned to a revision:

| Model | Licence | Pinned revision |
|---|---|---|
| `google/owlv2-base-patch16-ensemble` | Apache-2.0 | `cfd3195b` |
| `IDEA-Research/grounding-dino-tiny` | Apache-2.0 | `a2bb814d` |
| `depth-anything/Depth-Anything-V2-Metric-Indoor-Small-hf` | Apache-2.0 (see below) | `8078d68a` |

The Depth Anything metric model card does not state a licence itself. It is the Transformers
conversion of `depth-anything/Depth-Anything-V2-Metric-Hypersim-Small`, which is published under
Apache-2.0, and the Depth Anything V2 project licenses all Small models under Apache-2.0 (the
Base, Large and Giant models are CC-BY-NC-4.0 and are not used).

Ultralytics was removed from the code, configuration and install scripts.

## Consequences

Some strong models are off the table, and any new model needs a licence check before use. The
whole robot can be shipped or modified without licence obligations beyond attribution.
