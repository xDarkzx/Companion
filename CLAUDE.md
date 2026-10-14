# Instructions for coding agents

Follow [CONTRIBUTING.md](CONTRIBUTING.md): it is the rulebook for every change in this
repository, whether a person or an agent makes it. In short:

- Write the failing test first. Nothing is done until `bash scripts/docker_verify.sh` ends with
  `DONE_OK` and the relevant behaviour has been shown.
- Register every topic and service in `tools/companion_contracts.py`; regenerate the
  architecture diagram.
- No silent fallbacks, no unlicensed models, no `print()` in nodes, files under 800 lines.
- Architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Roadmap:
  [docs/ROADMAP.md](docs/ROADMAP.md).
