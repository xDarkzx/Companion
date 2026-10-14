# 0004. OWLv2 is the default detector

- Status: Accepted
- Date: 2026-10-15

## Context

Two Apache-2.0 open-vocabulary detectors are available behind the same `Detector` contract:
OWLv2 (base, patch 16, ensemble) and Grounding DINO tiny. The robot needs one default.

## Evidence

From [EVALUATION.md](../EVALUATION.md):

| Detector | NYU objects found (IoU ≥ 0.5) | Median 3D error, depth camera | COCO val2017 AP |
|---|---|---|---|
| OWLv2 | 77.1% of 2,062 | 5.4 cm | 43.6 (all 5,000 images) |
| Grounding DINO tiny | 75.0% of 2,062 | 5.4 cm | – |

COCO was benchmarked for the chosen default. On the household benchmark the two place objects equally well once found, and OWLv2 finds
slightly more of them. Grounding DINO also needs its prompt split into chunks once a query
list passes 256 tokens, which costs one forward pass per chunk on long watch lists.

## Decision

OWLv2 is the default (`backend: owlv2`). Grounding DINO stays available behind the same
parameter.

## Consequences

One detector to tune and document. Switching is a one-line configuration change, and the
benchmarks can be rerun for either backend with the scripts in `eval/`.
