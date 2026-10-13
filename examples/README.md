# Examples

Complete, validator-passing inputs for one Chinese and one English video. Copy their shape; do not copy their facts.

- `zh-meeting-brief/`: zh-CN, Chinese market
- `en-meeting-brief/`: en-US, US market

Each folder contains:

| File | Checked by |
|---|---|
| `script-package.json` | `scripts/validate_package.py` (with `claim-ledger.json`) |
| `claim-ledger.json` | `scripts/validate_package.py` |
| `timeline.json` | `scripts/audit_timeline.py` |
| `source-ledger.json` | `scripts/validate_sources.py` |

"Example Notes AI" and every `example.com` URL are placeholders. A real video must research the actual product and cite real sources.

Both examples end with the default ACEMODE brand card (56.5–60 s). The tests in `tests/test_skill.py` run every validator on these folders, so update the examples whenever a schema or limit changes.
