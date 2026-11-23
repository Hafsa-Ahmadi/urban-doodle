"""Descriptive distributions from either merged seed results or an automated run."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
outputs = ROOT / "outputs"
manual_path = outputs / "results.json"
automated_path = outputs / "automated_results.json"

if manual_path.exists():
    path = manual_path
elif automated_path.exists():
    path = automated_path
else:
    raise SystemExit(
        "No research results found. Run the agent first, or add outputs/results.json "
        "from the reviewed seed dataset."
    )

rows = json.loads(path.read_text(encoding="utf-8")).get("applications", [])
if not rows:
    raise SystemExit(f"No application rows found in {path}")

reviewed = [r for r in rows if r.get("research_status") == "manual_source_reviewed"]
population = reviewed if reviewed else rows
label = "manual source-reviewed subset" if reviewed else "automated dataset"
print(f"Source: {path.relative_to(ROOT)}")
print(f"Rows in file: {len(rows)}; rows used for metrics: {len(population)} ({label})")

fields = [
    "api_availability", "credential_acquisition", "mcp_status",
    "buildability", "priority", "authentication"
]
for field in fields:
    counts = Counter()
    for row in population:
        value = row.get(field, "Unknown")
        if isinstance(value, list):
            counts.update(value or ["Unknown"])
        else:
            counts.update([value or "Unknown"])
    print(f"\\n{field}")
    for name, count in counts.most_common():
        print(f"  {name}: {count}/{len(population)} ({count / len(population) * 100:.1f}%)")

print("\\nReminder: multi-label fields overlap. Keep the denominator visible and do not generalize a purposive subset to all 100.")
