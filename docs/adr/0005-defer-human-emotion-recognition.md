# 0005. Recognising human emotion from faces is deferred

- Status: Accepted
- Date: 2026-10-14

## Context

The original vision for Companion was a robot that notices when you are upset and responds
with empathy. The obvious implementation, a facial-expression classifier, has two problems.
Inferring inner emotional state from facial expressions is scientifically contested: the same
expression means different things across people and situations. And emotion recognition from
biometric data is restricted under the EU AI Act, and prohibited in workplaces and schools.

## Decision

Do not build facial emotion recognition now. The brain keeps its empathy logic and the
`HumanEmotion` contract, fed by a stub node, so the behaviour layer can be developed and tested.
Any future sensing will start from what a person explicitly says ("I'm having a bad day"),
which needs no inference about their face.

## Consequences

The empathy layer is developed and tested against a stub input until spoken cues replace it. The project avoids shipping a
capability that would be unreliable and, in some settings, unlawful.
