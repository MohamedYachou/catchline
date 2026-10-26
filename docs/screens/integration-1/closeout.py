"""Audit existing evidence and write final receipts; never launch Unity or Git."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[2]
stamp = datetime.now(timezone.utc).isoformat()

def read(name):
    raw = (out / name).read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return raw.decode(encoding, errors="replace")

def data(name):
    return json.loads(read(name))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

verification = data("verification.json")
assert not verification["productionDrift"]
assert len(verification["gameSourceMatches"]) == 146
assert all(item["matches"] for item in verification["gameSourceMatches"])
assert len(verification["images"]) == 16
assert all(sha(out / item["path"]) == item["sha256"] for item in verification["images"])
meta = data("meta-audit.json")
assert not meta["missingMetas"] and not meta["duplicateGuids"]
assert data("native-exit.json")["exitCode"] == 0
assert data("native-initial-exit.json")["exitCode"] == 8
assert "INTEGRATION NATIVE COMPLETE" in read("native.log")
assert "TEST / no save reads or writes" in read("native.log")
assert "CREW ABILITY INTEGRATION REGRESSION PASSED" in read("check-integration-regression.log")
assert "Verified integration-regression (Unity exit 0)" in read("regression-wrapper.log")
assert "Verified integration-native-retry (Unity exit 0)" in read("native-retry-build-wrapper.log")
assert data("strike-fx/checks.json")["assertions"] == 88
assert data("pets/checks.json")["assertions"] == 66902
assert data("map10-checks.json")["hullRoutes"] == 600

processes = {
    "auditedUtc": stamp,
    "note": "No processes rerun at closeout. Wrapper codes are preserved from the execution checkpoint in comms.md; saved logs/JSON independently support the listed outcomes. Individual suites share the initial Unity process and have suite results, not separate process exit codes.",
    "processes": [
        {"name": "initial combined scratch build/suites", "unityExitCode": 0, "wrapperExitCode": 1, "evidence": ["check-integration-1.log", "wrapper.log", "suites.tsv", "initial-build.txt"], "result": "Build succeeded; retained initial regression exception and stale MAP9 assertion prevent a clean pass."},
        {"name": "initial native session", "processExitCode": 8, "evidence": ["native-initial-exit.json", "native-initial.log"], "result": "Scratch fixture counted pets before deferred destruction completed; no frames."},
        {"name": "corrected scratch native build", "unityExitCode": 0, "wrapperExitCode": 0, "evidence": ["check-integration-native-retry.log", "native-retry-build-wrapper.log", "map10-build.txt"]},
        {"name": "full original-wrapper regression", "unityExitCode": 0, "wrapperExitCode": 0, "evidence": ["check-integration-regression.log", "regression-wrapper.log", "integration-regression.json"]},
        {"name": "corrected native session", "processExitCode": 0, "wrapperExitCode": 0, "evidence": ["native-exit.json", "native-wrapper.log", "native.log", "capture-complete.txt"]},
    ],
}
(out / "process-exits.json").write_text(json.dumps(processes, indent=2) + "\n", encoding="utf-8")

images = []
for item in verification["images"]:
    path = item["path"]
    if path.startswith("pets/"):
        finding = "Dog on quay and ginger cat on crate visible in editor staging; closeups establish appearance and support contact. Phone overview pets are small."
    elif path.startswith("strike-fx/"):
        finding = "Editor TAP burst and separate mint ring visible; ripple frames remove TAP and show the strike effect."
    elif path.startswith("chart-"):
        finding = "Whale shelf and Seal cliffs pins and labels distinct, clear of named neighbouring cards."
    elif path.startswith("harbour-pets-"):
        finding = "Native tier-five overview: pet objects pass assertions but too small/occluded to identify confidently. Visual acceptance remains QUESTION."
    else:
        finding = "Native Seal cliffs arch-pool: readable TAP and bobber ring before strike; TAP removed and ripple visible after strike. Arch dominates upper framing; terrain/camera acceptance not established."
    images.append({**item, "openedIndividually": True, "reviewedUtc": stamp, "finding": finding})
review = {
    "owner": "Codex 1 (Windows app)", "reviewedUtc": stamp,
    "status": "Verification delivered with outstanding lead questions; not an unconditional integration pass.",
    "images": images,
    "questions": [
        {"file": "Assets/Editor/WhaleShelfMapChecks.cs:37", "finding": "Unchanged legacy checker requires nine maps; current tree has ten. MAP9-specific assertions after that gate did not execute."},
        {"file": "harbour-pets-1440.png / harbour-pets-844.png", "finding": "Native pet appearance cannot be confirmed confidently in these tier-five overview frames; editor appearance and native object-count checks pass."},
    ],
    "deviations": ["Two standalone builds and two native launches; initial scratch setup failures preserved. No production correction."],
    "limits": ["No production/source/asset edits or Git mutations.", "No installed-player, physical-device/touch, listening or Mo acceptance.", "Inventory and shared patch are the pre-check snapshot; peer changes after that snapshot require lead review before staging."],
}
(out / "review.json").write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")

missing = []
for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", read("README.md")):
    if not target.startswith(("https:", "http:", "#")) and not (out / target).exists():
        missing.append(target)
assert not missing, missing
print("Closeout PASS: 16 reviewed image hashes, 146 source matches, zero drift; report links resolve; receipts written.")
