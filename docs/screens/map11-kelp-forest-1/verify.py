"""Verify saved MAP11 delivery receipts without rerunning Unity."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]


def read(name):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = read("checks.json")
    assert (checks["maps"], checks["hullRoutes"], checks["lanes"]) == (11, 660, 33)
    assert all(checks[key] for key in ("assets", "chartPurchase", "anchors", "groundPoolsReady"))
    assert len(checks["trips"]) == 4
    final = read("final-checks.json")
    assert (final["maps"], final["hullRoutes"], final["lanes"]) == (11, 60, 33)
    assert final["chartPurchase"] and len(final["trips"]) == 4
    assert read("native-exit.json")["exitCode"] == 0
    exits = read("process-exits.json")
    assert all(exits[key] == 0 for key in ("buildWrapper", "buildUnity", "nativeWrapper", "regressionWrapper", "regressionUnity"))
    regression = (EVIDENCE / "regression.log").read_text(encoding="utf-8-sig")
    assert "CREW ABILITY INTEGRATION REGRESSION PASSED" in regression
    run = read("native-run.json")
    assert run["sessionOnly"] and not run["mainDriftAtLaunch"]
    review = read("review.json")
    assert len(review["images"]) == 10
    for entry in review["images"]:
        path = EVIDENCE / entry["file"]
        assert sha(path) == entry["sha256"], path
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert [int.from_bytes(data[i:i+4], "big") for i in (16, 20)] == entry["dimensions"]
    meta = read("meta-audit.json")
    assert not meta["missingMetas"] and not meta["duplicateGuids"]
    art_dir = ROOT / "Art/Models/Maps/GullKelpForest"
    art = json.loads((art_dir / "art-receipt.json").read_text())
    for entry in art["files"]:
        assert sha(ROOT / entry["file"]) == entry["sha256"], entry["file"]
    art_review = json.loads((art_dir / "art-review.json").read_text())
    assert len(art_review["images"]) == 18
    for entry in art_review["images"]:
        assert entry["opened"] and sha(art_dir / entry["file"]) == entry["sha256"]
    drift = []
    for entry in run["sourceHashes"]:
        path = ROOT / entry["path"]
        if not path.exists() or sha(path).lower() != entry["sha256"].lower():
            drift.append(entry["path"])
    # Peer changes after capture are reported, never silently presented as tested.
    result = {"utc": datetime.now(timezone.utc).isoformat(), "passed": True,
              "nativeImages": 10, "nativeSources": run["sourceCount"],
              "postCaptureSourceDrift": drift,
              "limits": ["Saved receipt/hash verification; no installed-player or touch acceptance.",
                         "Foreground-post broad-circle exception remains a lead review question."]}
    (EVIDENCE / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
