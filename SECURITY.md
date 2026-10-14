# Security

## Reporting

Please report security issues privately through GitHub's
[private vulnerability reporting](https://github.com/xDarkzx/Companion/security/advisories/new),
not in a public issue. You will get a reply within a week.

## Design notes

- **Offline by default.** Speech, perception and replies run locally. The optional LLM is a
  local Ollama server; no audio, images or text leave the machine unless you configure that.
- **Memory stays local and bounded.** Learned facts go into a local SQLite file
  (`~/.companion/facts.db`) with a fixed row cap. Treat it as personal data: don't commit it,
  and wipe it before handing the robot to someone else.
- **No secrets in the repository.** CI scans the full git history with gitleaks, and a
  pre-commit hook does the same locally.
- **Robot safety.** Models never command motors. Motion goes through Nav2 and the body's
  firmware, and "stop" cancels any plan or goal in flight.
