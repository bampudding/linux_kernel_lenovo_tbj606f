#!/usr/bin/env python3
"""Record published TB-J606F GitHub release assets and source tag commits."""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def github_pages(repo):
    response = subprocess.check_output([
        "gh", "api", "--paginate", f"repos/{repo}/releases?per_page=100"
    ], text=True)
    decoder = json.JSONDecoder()
    offset = 0
    records = []
    while offset < len(response):
        while offset < len(response) and response[offset].isspace():
            offset += 1
        if offset == len(response):
            break
        page, offset = decoder.raw_decode(response, offset)
        if not isinstance(page, list):
            raise ValueError("unexpected GitHub response: expected release array")
        records.extend(page)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="bampudding/linux_kernel_lenovo_tbj606f")
    parser.add_argument("--output", type=Path, default=Path(
        "Documentation/tbj606f/archive/github-release-catalog.json"))
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("invalid GitHub owner/repository")
    releases = github_pages(args.repo)
    rows = []
    missing_digests = []
    for release in releases:
        tag = release["tag_name"]
        if not re.fullmatch(r"[A-Za-z0-9_.\-/]+", tag):
            raise ValueError("unsafe release tag name: " + tag)
        try:
            commit = git("rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
        except subprocess.CalledProcessError as error:
            raise RuntimeError("GitHub release tag missing locally: " + tag) from error
        parents = git("rev-list", "--parents", "-n", "1", commit).split()[1:]
        assets = []
        for asset in sorted(release["assets"], key=lambda item: item["name"]):
            digest = asset.get("digest")
            if not isinstance(digest, str) or not digest.startswith("sha256:"):
                missing_digests.append(f"{tag}/{asset['name']}")
            assets.append({
                "name": asset["name"],
                "size_bytes": asset["size"],
                "sha256": digest.removeprefix("sha256:") if digest else None,
                "download_url": asset["browser_download_url"],
            })
        rows.append({
            "tag": tag,
            "source_commit": commit,
            "first_parent": parents[0] if parents else None,
            "single_commit_range": f"{parents[0]}..{commit}" if parents else None,
            "source_subject": git("log", "-1", "--format=%s", commit),
            "release_name": release["name"],
            "published_at": release["published_at"],
            "release_url": release["html_url"],
            "release_notes_sha256": hashlib.sha256(release["body"].encode()).hexdigest(),
            "assets": assets,
        })
    rows.sort(key=lambda release: (release["published_at"], release["tag"]))
    catalog = {
        "schema_version": 1,
        "repository": args.repo,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "release_count": len(rows),
        "asset_count": sum(len(row["assets"]) for row in rows),
        "notes": [
            "The GitHub asset digest provides the published SHA256; source_commit resolves the actual tag, even if GitHub target_commitish refers to a branch.",
            "single_commit_range denotes only the final commit and its first parent, not the complete milestone development interval.",
            "Release notes are available at release_url and identified by release_notes_sha256.",
            "GitHub assets and this metadata do not independently archive local proprietary, test, and diagnostic files.",
        ],
        "missing_sha256_digests": missing_digests,
        "releases": rows,
    }
    output = args.output.resolve()
    if not output.parent.is_dir():
        parser.error("output parent directory missing")
    descriptor, temporary = tempfile.mkstemp(prefix=".p11-release-index-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(catalog, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Catalogued {len(rows)} releases and {catalog['asset_count']} assets", flush=True)
    if missing_digests:
        print("WARNING: missing GitHub digest for: " + ", ".join(missing_digests),
              file=sys.stderr)


if __name__ == "__main__":
    main()
