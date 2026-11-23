"""Score automated verification outcomes without overstating accuracy."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "outputs" / "automated_verification.json"
if not path.exists():
    raise SystemExit("No automated_verification.json. Run agent/research_agent.py first.")

records = json.loads(path.read_text(encoding="utf-8")).get("verification", [])
checks = [check for row in records for check in row.get("claim_checks", [])]
labels = ["Correct", "Partially Correct", "Incorrect", "Unverifiable"]
counts = {label: sum(check.get("outcome") == label for check in checks) for label in labels}
resolved = counts["Correct"] + counts["Incorrect"]

print(f"Claims checked: {len(checks)}")
for label in labels:
    print(f"{label}: {counts[label]}")
if resolved:
    print(f"Strict accuracy among binary-resolvable claims: {counts['Correct']}/{resolved} = {counts['Correct']/resolved:.1%}")
else:
    print("Strict accuracy: not measurable (no binary-resolvable claims).")
print("Partial and unverifiable claims are reported separately, not counted as correct.")
