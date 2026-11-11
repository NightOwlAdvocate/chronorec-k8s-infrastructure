# Security and data boundary

This repository is a local infrastructure lab, not a production health product.

- Do not submit real names, voice recordings, sleep logs, mood logs, medical
  information, credentials, kubeconfig files, tokens, or exported Secrets.
- Use only the static synthetic dataset included in the demo API.
- Run failure-injection commands only against `kind-chronorec-lab`.
- Do not expose port-forwards to public interfaces.
- If a secret is committed, revoke it first and then remove it from Git history.

Security reports should describe the affected file and reproduction steps without
including personal data or live credentials.
