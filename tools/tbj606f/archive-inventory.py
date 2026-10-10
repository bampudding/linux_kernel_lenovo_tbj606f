#!/usr/bin/env python3
"""Inventory archived TB-J606F files by SHA256 without changing source files."""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


FIRMWARE = (
    "firmware/zui12.0.519/TB-J606F_CN_WIFI_USER_Q00016.0_Q_ZUI_12.0.519_ST_210130.zip",
    "firmware/zui12.0.519/vendor_a.raw.img",
    "firmware/zui14.0.147/08_TB-J606F_CN_WIFI_USER_ZUI_13.1.580_to_TB-J606F_CN_WIFI_USER_ZUI_14.0.147.zip",
    "firmware/zui14.0.147/payload.bin",
    "firmware/zui14.0.147/extracted-dsp-test/dsp.img",
    "firmware/service/TB-J606F_USR_S010534_2302101738_PRC.rar",
)


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/root/HDD/user0/P11"))
    parser.add_argument("--output", type=Path, default=Path(
        "Documentation/tbj606f/archive/hdd-artifact-manifest.json"))
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error("manifest output must be outside the archive tree")
    if not output.parent.is_dir():
        parser.error("manifest output parent directory missing")

    tags = set(subprocess.check_output(["git", "tag", "-l"], text=True).splitlines())
    candidates = []
    for directory in ("releases", "experiments"):
        tree = root / directory
        if not tree.is_dir():
            parser.error("required archive directory missing: " + str(tree))
        for base, subdirs, names in os.walk(tree, followlinks=False):
            subdirs.sort()
            for name in sorted(names):
                candidates.append(Path(base) / name)
            for name in subdirs:
                possible_link = Path(base) / name
                if possible_link.is_symlink():
                    candidates.append(possible_link)
    for name in FIRMWARE:
        path = root / name
        if not path.is_file():
            parser.error("required firmware input missing: " + str(path))
        candidates.append(path)

    entries = []
    total_bytes = 0
    link_count = 0
    for index, path in enumerate(sorted(set(candidates)), 1):
        relative = path.relative_to(root).as_posix()
        parts = relative.split("/")
        release = None
        if len(parts) >= 3 and parts[0] == "releases":
            potential = parts[2] if parts[1] == "github" else parts[1]
            if potential in tags:
                release = potential
        keep = parts[0] == "firmware" or (
            parts[0] == "releases" and parts[1] == "github")
        entry = {
            "path": relative,
            "release_association": release,
            "cleanup_recommendation": "keep" if keep else "retain_until_archive_verified",
        }
        if path.is_symlink():
            entry.update({
                "entry_type": "symlink",
                "link_target": os.readlink(path),
                "size_bytes": 0,
                "sha256": None,
            })
            link_count += 1
        else:
            if not path.is_file():
                parser.error("non-regular archive entry: " + str(path))
            before = path.stat()
            digest = checksum(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (
                    after.st_size, after.st_mtime_ns, after.st_ino):
                parser.error("archive entry changed during hashing: " + str(path))
            entry.update({
                "entry_type": "file", "size_bytes": before.st_size, "sha256": digest,
            })
            total_bytes += before.st_size
        entries.append(entry)
        if index % 100 == 0 or index == len(candidates):
            print(f"Hashed {index}/{len(candidates)} files ({total_bytes} bytes)",
                  file=sys.stderr, flush=True)

    manifest = {
        "schema_version": 1,
        "device": "Lenovo P11 TB-J606F",
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "archive_root": str(root),
        "included_trees": ["releases", "experiments"],
        "included_individual_firmware_paths": list(FIRMWARE),
        "file_count": len(entries),
        "symlink_count": link_count,
        "total_file_bytes": total_bytes,
        "notes": [
            "Only the specified archive trees and selected firmware inputs are inventoried; the larger extracted firmware tree is excluded.",
            "Release association is assigned only for a folder name that matches a local Git tag.",
            "Symlink targets are recorded as link text without following or hashing their target contents.",
            "A checksum manifest does not back up bytes; no cleanup is authorized without verified separate copies.",
            "Proprietary-containing artifacts are described by hash without granting redistribution rights.",
            "The Mac-hosted GSI is deliberately neither scanned nor copied by this utility.",
        ],
        "files": entries,
    }
    content = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    fd, temporary = tempfile.mkstemp(prefix=".p11-inventory-", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Wrote {output}: {len(entries)} entries; {total_bytes} bytes", flush=True)


if __name__ == "__main__":
    main()
