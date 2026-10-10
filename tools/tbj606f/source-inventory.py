#!/usr/bin/env python3
"""Hash published TB-J606F source helpers/docs for archive reconciliation."""

import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


OUTPUT = Path("Documentation/tbj606f/archive/legacy-archive-manifest.json")


def main():
    paths = subprocess.check_output([
        "git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
        "--", "Documentation/tbj606f", "tools/tbj606f",
    ]).split(b"\0")
    files = []
    for raw in sorted(set(paths)):
        if not raw:
            continue
        name = os.fsdecode(raw)
        if name == OUTPUT.as_posix():
            continue  # a manifest cannot meaningfully checksum its own contents
        path = Path(name)
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("unexpected nonregular source entry: " + name)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                digest.update(chunk)
        files.append({
            "path": name,
            "size_bytes": path.stat().st_size,
            "sha256": digest.hexdigest(),
            "release_association": "repository source history",
            "recommendation": "keep",
        })
    record = {
        "schema_version": 2,
        "device": "Lenovo P11 TB-J606F",
        "repository": "bampudding/linux_kernel_lenovo_tbj606f",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "purpose": "Source documentation and helper checksums before legacy cleanup",
        "notes": [
            "This manifest excludes itself to avoid a cyclic checksum.",
            "The full kernel source is preserved by Git commits and tags, not duplicated here as per-file hashes.",
            "See hdd-artifact-manifest.json for HDD artifact/firmware checksums and github-release-catalog.json for published assets.",
        ],
        "files": files,
    }
    output = OUTPUT.resolve()
    descriptor, temp = tempfile.mkstemp(prefix=".p11-source-inventory-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, output)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(f"Recorded {len(files)} source helper/documentation files")


if __name__ == "__main__":
    main()
