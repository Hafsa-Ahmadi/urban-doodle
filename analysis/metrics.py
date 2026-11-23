import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "outputs" / "results.json").read_text(encoding="utf-8"))["applications"]
reviewed = [r for r in rows if r.get("research_status") == "manual_source_reviewed"]

print(f"Scope: {len(rows)} apps; evidence-reviewed: {len(reviewed)}; pending: {len(rows)-len(reviewed)}")
for field in ["api_availability", "access_class", "mcp_status", "buildability", "priority", "auth_families", "blocker_families"]:
    counts = Counter()
    for row in reviewed:
        value = row.get(field, "Unknown")
        counts.update(value if isinstance(value, list) else [value])
    print(f"\n{field}")
    for label, count in counts.most_common():
        pct = count / len(reviewed) * 100 if reviewed else 0
        print(f"  {label}: {count}/{len(reviewed)} ({pct:.1f}%)")
print("\nAgent accuracy: NOT MEASURED until automated pass 1 and independent pass 2 complete.")
