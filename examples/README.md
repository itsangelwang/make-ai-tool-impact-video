# Examples

A complete, validator-passing input for one video. Copy its shape; do not copy its facts.

- `en-meeting-brief/`: en-US, US market

The folder contains:

| File | Checked by |
|---|---|
| `script-package.json` | `scripts/validate_package.py` (with `claim-ledger.json`) |
| `claim-ledger.json` | `scripts/validate_package.py` |
| `timeline.json` | `scripts/audit_timeline.py` |
| `source-ledger.json` | `scripts/validate_sources.py` |

"Example Notes AI" and every `example.com` URL are placeholders. A real video must research the actual product and cite real sources.

The example ends with the default ACEMODE brand card (56.5–60 s). The tests in `tests/test_skill.py` run every validator on this folder, so update the example whenever a schema or limit changes.
