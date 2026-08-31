### Overview

**Strix Safe** disables telemetry by default. Upstream Strix can collect anonymized usage data via [PostHog](https://posthog.com) and [Scarf](https://scarf.sh); this fork does not send those beacons unless you opt in.

You can review the source ([posthog.py](./posthog.py), [scarf.py](./scarf.py)) to see exactly what would be tracked when enabled.

### Telemetry Policy (when enabled)

Privacy is our priority. All collected data is anonymized by default. Each session gets a random UUID that is not persisted or tied to you. Your code, scan targets, vulnerability details, and findings always remain private and are never collected.

### What We Track (only if opted in)

We collect only very **basic** usage data including:

**Session Errors:** Duration and error types (not messages or stack traces)\
**System Context:** OS type, architecture, Strix version\
**Scan Context:** Scan mode (quick/standard/deep), scan type (whitebox/blackbox)\
**Model Usage:** Which LLM model is being used and whether it runs via an API key or a model subscription (not prompts or responses)\
**Feature Usage:** Which built-in skills are loaded\
**Aggregate Metrics:** Vulnerability counts by severity and weakness category (CWE)

### What We **Never** Collect

- Usernames, or any identifying information
- Scan targets, file paths, target URLs, or domains
- Vulnerability details, descriptions, or code
- LLM requests and responses

### Defaults in Strix Safe

Telemetry is **off** by default. To opt in:

```bash
export STRIX_TELEMETRY=1
```

To keep it off explicitly:

```bash
export STRIX_TELEMETRY=0
```
