#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Audit GitHub releases against local Git tags and the archived HDD inventory.

Read-only for GitHub, HDD and source; outputs ONLY the named audit JSON/Markdown.
No device commands, flashing, rebuilding or large asset downloads.
"""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPO = "bampudding/linux_kernel_lenovo_tbj606f"
ROOT = Path("Documentation/tbj606f/archive")
SPECIAL = {
"zui12-65hz-probe-20260917": "65 Hz probe; later reverted by 4.19.96 60 Hz tag; experiment",
"zui12-next-tested-20260917": "65 Hz probe lineage; subsequent revert means not retained 60 Hz baseline",
"zui12-post157-eas-idle-opt14-known-good-20260922": "historical known-good scheduler checkpoint; no exact-tag HDD build set",
"zui12-post157-gpu-oc15-980-failed-20260922": "explicit FAILED 980 MHz GPU experiment; not a tested image",
"zui12-post157-gpu-oc16-harness-built-20260922": "GPU override harness BUILT; not proof of runtime success",
"zui12-post157-gpu-oc17-native960-tested-20260922": "historical guarded 960 MHz GPU opt-in; not default clock",
"zui12-post157-f2fs-compression-core-off-build-20260918": "compression core-off BUILD checkpoint; no enabled-runtime claim",
"zui12-post157-erofs-lineage23.2-built-20260922": "BUILD checkpoint; shares commit with tested/runtime-tested tags",
"zui12-post157-erofs-lineage23.2-tested-20260922": "historical tested label; shares commit with built/runtime-tested tags",
"zui12-post157-erofs-lineage23.2-runtime-tested-20260922": "historical EROFS runtime milestone; shares sibling commit",
"tbj606f-erofs-lz4-v183-20260924": "LZ4 decoder source checkpoint; release explicitly disclaims full boot",
"p11-zui14-adsp-fastrpc-sensors-tested-20260923": "partial ADSP/sensors milestone; not final validated hybrid",
"tbj606f-a16-zui14-kernel-stable-20260924": "stable kernel source; binaries later released in v1",
"tbj606f-a16-zui14-opensource-20260924": "source/publication milestone; no GitHub kernel image",
"tbj606f-a16-zui14-published-20260924": "source/publication milestone; no GitHub kernel image",
"tbj606f-a16-zui14-public-v1": "validated kernel/ABI payload; owner must supply and repack boot",
"tbj606f-a16-zui14-public-v2": "installer/docs ONLY; get kernel payload from v1/v3",
"tbj606f-a16-zui14-public-v3": "source-matched v1-identical kernel + helper bundle; no OEM images",
"tbj606f-a16-zui14-public-v4": "single ZIP plus checksum, historic pre-reconstruction kit; owner input still required",
}
def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()

def gh_releases():
    raw = subprocess.check_output(
        ["gh", "api", "--paginate", f"repos/{REPO}/releases?per_page=100"],
        text=True)
    decoder = json.JSONDecoder()
    pos, rows = 0, []
    while pos < len(raw):
        while pos < len(raw) and raw[pos].isspace():
            pos += 1
        if pos == len(raw):
            break
        page, pos = decoder.raw_decode(raw, pos)
        if not isinstance(page, list):
            raise ValueError("GitHub release API returned non-list page")
        rows.extend(page)
    return rows

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-output", type=Path,
                    default=ROOT / "release-reproducibility-audit.json")
    ap.add_argument("--markdown-output", type=Path,
                    default=ROOT / "release-reproducibility-audit.md")
    opts = ap.parse_args()
    old = json.loads((ROOT / "github-release-catalog.json").read_text())
    manifest = json.loads((ROOT / "hdd-artifact-manifest.json").read_text())
    if manifest["archive_root"] != "/root/HDD/user0/P11":
        raise ValueError("HDD manifest has unexpected root")
    sha_paths = collections.defaultdict(list)
    stage = collections.defaultdict(list)
    for f in manifest["files"]:
        if f["entry_type"] != "file":
            continue
        if f.get("sha256"):
            sha_paths[f["sha256"]].append(f["path"])
        parts = f["path"].split("/")
        if len(parts) > 2 and parts[0] == "releases":
            stage[parts[1]].append(f)
    rows, commit_aliases, missing = [], collections.defaultdict(list), []
    # Intentionally preserve the pre-v5 publication window when v5 is live.
    for r in sorted(gh_releases(), key=lambda x:(x["published_at"],x["tag_name"])):
        tag = r["tag_name"]
        if tag == "tbj606f-a16-zui14-public-v5":
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", tag):
            raise ValueError("unsafe release tag")
        commit = git("rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
        commit_aliases[commit].append(tag)
        assets = []
        for asset in sorted(r["assets"], key=lambda a:a["name"]):
            digest = asset.get("digest") or ""
            if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                missing.append(tag+"/"+asset["name"])
            checksum = digest.removeprefix("sha256:") if digest else None
            assets.append({
                "name": asset["name"], "size_bytes":asset["size"],
                "github_sha256":checksum, "url":asset["browser_download_url"],
                "hdd_same_sha256_paths":sha_paths.get(checksum, []),
            })
        # Check separately downloadable installer/helper bytes against the
        # immutable Git TAG tree, not the concurrently edited working tree.
        # A v2 release attachment can exist even when the v2 tag lacks it.
        tag_blob_assets = {}
        map_path = {
            "install.sh":"tools/tbj606f/install.sh",
            "installation.md":"Documentation/tbj606f/installation.md",
            "repack-boot.sh":"tools/tbj606f/repack-boot.sh",
            "make-hybrid-vendor.sh":"tools/tbj606f/make-hybrid-vendor.sh",
            "mkbootimg.py":"tools/tbj606f/mkbootimg.py",
            "unpack_bootimg.py":"tools/tbj606f/unpack_bootimg.py",
        }
        if tag.endswith(("public-v2","public-v3","public-v4")):
            for asset in assets:
                if asset["name"] not in map_path:
                    continue
                try:
                    blob = subprocess.check_output([
                        "git","show",f"refs/tags/{tag}:{map_path[asset['name']]}"],
                        stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    tag_blob_assets[asset["name"]] = {
                        "tag_file":"absent from release source tag",
                        "matches_published_asset":False}
                else:
                    sha = hashlib.sha256(blob).hexdigest()
                    tag_blob_assets[asset["name"]] = {
                        "tag_file":map_path[asset["name"]],
                        "tag_blob_sha256":sha,
                        "matches_published_asset":sha==asset["github_sha256"]}
        local = stage.get(tag, [])
        names = {Path(f["path"]).name for f in local}
        images = [f["path"] for f in local if Path(f["path"]).name=="Image"]
        boots = [f["path"] for f in local if f["path"].endswith(".img")
                 and Path(f["path"]).name.startswith("boot")]
        configs = [f["path"] for f in local
                   if Path(f["path"]).name in ("config","kernel.config",".config")]
        symbols = [f["path"] for f in local if Path(f["path"]).name=="Module.symvers"]
        source = next((a for a in assets if a["name"].endswith("-source.tar.gz")),None)
        if tag.endswith("public-v4"):
            expect={"tbj606f-a16-zui14-public-v4-flash-kit.zip",
                    "tbj606f-a16-zui14-public-v4-SHA256SUMS.txt"}
            if len(assets)!=2 or {a["name"] for a in assets}!=expect:
                raise ValueError("v4 release assets differ from the verified two-file publication")
            cls="single-flash-kit-zip-and-checksum"
        elif tag.endswith("public-v3"):
            cls="kernel-and-helper-bundle"
        elif tag.endswith("public-v1"):
            cls="kernel-abi-bundle"
        elif tag.endswith("public-v2"):
            cls="installer-only"
        elif source and len(assets)==4:
            expected={source["name"],"SHA256SUMS","VERSION.txt","commit-stat.txt"}
            cls="source-and-metadata-only" if {a["name"] for a in assets}==expected else "other"
        else:
            cls="other"
        notes = SPECIAL.get(tag)
        if notes is None:
            if any("VALIDATION" in n.upper() for n in names):
                notes="historical tested tag + local validation note; no fresh device run"
            elif "tested" in tag:
                notes="historical tested tag label; no fresh device run"
            else:
                notes="historical source checkpoint; no fresh device run"
        rows.append({
            "tag":tag, "source_commit":commit,
            "source_commit_url":f"https://github.com/{REPO}/commit/{commit}",
            "release_url":r["html_url"],"published_at":r["published_at"],
            "release_notes_sha256":hashlib.sha256(
                (r.get("body") or "").encode()).hexdigest(),
            "class":cls, "source_tar_sha256":source["github_sha256"] if source else None,
            "assets":assets,
            "tag_source_blob_comparison":tag_blob_assets,
            "hdd_exact_tag_stage_files":[f["path"] for f in local],
            "hdd_image":images,"hdd_boot":boots,"hdd_config":configs,
            "hdd_module_symvers":symbols,
            "hdd_exact_tag_complete_set":bool(images and boots and configs and symbols),
            "hdd_validation_notes":[f["path"] for f in local
                if "VALIDATION" in Path(f["path"]).name.upper()],
            "disposition":notes,
            "source_snapshot_proves_binary_reproduction":False,
            "public_directly_flashable_oem_image":False,
        })
    if len(set(r["tag"] for r in rows)) != len(rows):
        raise ValueError("duplicate release tag")
    if "tbj606f-a16-zui14-public-v4" not in {r["tag"] for r in rows}:
        raise ValueError("pre-v5 audit requires published v4 two-asset release")
    types = collections.Counter(r["class"] for r in rows)
    source_local = sum(r["class"]=="source-and-metadata-only"
                       and r["hdd_exact_tag_complete_set"] for r in rows)
    matches = sum(bool(a["hdd_same_sha256_paths"]) for r in rows
                  for a in r["assets"])
    summary = {
        "github_release_count":len(rows),
        "github_asset_count":sum(len(r["assets"]) for r in rows),
        "missing_github_sha256_asset_count":len(missing),
        "local_resolved_release_tag_count":len(rows),
        "distinct_release_source_commit_count":len(commit_aliases),
        "asset_class_counts":dict(sorted(types.items())),
        "source_only_with_exact_hdd_image_boot_config_symvers":source_local,
        "source_only_without_exact_hdd_image_boot_config_symvers":
            types["source-and-metadata-only"]-source_local,
        "published_assets_with_matching_old_hdd_sha256":matches,
        "public_directly_flashable_oem_boot_vendor_or_gsi_releases":0,
        "fresh_binary_reproduction_proven_by_this_audit":0,
    }
    out = {
        "schema_version":1,
        "generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repository":REPO,
        "source":"live GitHub asset API, local peeled tag commits, archived HDD SHA256 manifest",
        "hdd_manifest_generated_utc":manifest["generated_utc"],
        "old_github_catalog_generated_utc":old["generated_utc"],
        "old_github_catalog_release_count":old["release_count"],
        "old_github_catalog_asset_count":old["asset_count"],
        "audit_cutoff":"pre-v5 (v4 included; v4 historic 57-release snapshot unchanged)",
        "zui12_stock_qfil_boot_sha256":"d4e86ef850d4109a8b2b7a87bec82dd2c60cc68a6f0e3709e7bec0f74ff982d8",
        "stable_boot_sha256":"93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635",
        "stable_boot_size_bytes":14286848,
        "post_v4_source_to_stable_boot_reconstruction_proven":True,
        "summary":summary,"missing_sha256_assets":missing,
        "source_commit_alias_groups":[v for v in commit_aliases.values() if len(v)>1],
        "limits":[
            "GitHub digests come from asset API metadata; not all assets were downloaded and rehashed.",
            "HDD manifest SHA256 records were generated previously, not rehashed now.",
            "Source tar/tag != exact rebuilt binary: toolchains, configs, signing keys and firmware matter.",
            "Historical tested names are not fresh device checks.",
            "Local HDD boot images and OEM vendor are not publicly distributed.",
            "No device, build, flash, firmware extraction or HDD deletion was run.",
        ],"releases":rows,
    }
    opts.json_output.parent.mkdir(parents=True,exist_ok=True)
    opts.json_output.write_text(json.dumps(out,indent=2)+"\n")
    t=chr(96)
    lines=["# TB-J606F release reproducibility and flash-asset audit","",
           f"Generated {out['generated_utc']}. Full digests, download URLs, and HDD paths:",
           "[JSON report](release-reproducibility-audit.json).","",
           "## All public releases (one row per tag)","",
           "The source SHA is a prefix of GitHub asset metadata, not an independent downloaded hash.",
           "HDD local means the EXACT tag-named stage folder contains Image + boot image + config + Module.symvers.",
           "All historical runtime classifications refer to archival claims, not new device tests.","",
           "| Release | Source commit | GitHub asset classification | Source SHA | Exact-tag HDD | Historical disposition |",
           "|---|---|---|---|---|---|"]
    v4 = next(x for x in rows if x["tag"] == "tbj606f-a16-zui14-public-v4")
    v4_assets = {a["name"]: a for a in v4["assets"]}
    v4_zip = v4_assets["tbj606f-a16-zui14-public-v4-flash-kit.zip"]
    v4_sum = v4_assets["tbj606f-a16-zui14-public-v4-SHA256SUMS.txt"]
    introduction = f"""
## Scope and exact counts

The live [release index](https://github.com/{REPO}/releases) contains **{len(rows)} releases
with {summary['github_asset_count']} downloadable asset records**. All {len(rows)}
release tag names resolve locally, but they identify only **{len(commit_aliases)}
distinct source commits**. GitHub supplies a SHA256 digest for all
{summary['github_asset_count']} assets (missing: {len(missing)}). The API reports
metadata and asset digests; this audit did not download and rehash {summary["github_asset_count"]} assets or
all approximately 180 MB source tarballs.

- **{types['source-and-metadata-only']} source-and-metadata-only releases**:
  each has only a source tar.gz, VERSION.txt, commit-stat.txt and SHA256SUMS.
  Their public downloads contain **zero directly deployable kernel/boot images**.
- **1 public kernel+ABI release (v1)**: raw Image/Image.gz, exact config,
  Module.symvers, System.map, compatibility module and checksums.
- **1 installer-only release (v2)**: install.sh, documentation, bundle and
  checksums; **no kernel Image**. The release ZIP/tar archive filename contains
  the published spelling tbj6066f, preserved as historical evidence.
- **1 source-matched bundle (v3)**: the same validated v1 kernel bytes and
  compatibility module, plus boot/vendor reconstruction scripts and manifests.
  Published v3 installer and guide hashes match the v3 *Git tag* blobs.
{("- **1 v4 release with exactly 2 public assets**: the single non-proprietary deployment ZIP named " + chr(96) + "tbj606f-a16-zui14-public-v4-flash-kit.zip" + chr(96) + " and its external checksum file " + chr(96) + "tbj606f-a16-zui14-public-v4-SHA256SUMS.txt" + chr(96) + ". The ZIP includes validated kernel payload and helpers; it excludes proprietary OEM boot/vendor and the GSI." if types["single-flash-kit-zip-and-checksum"] else "")}
- **0 GitHub releases with a ready-to-flash OEM boot.img, vendor.img or Android
  GSI**. An arm64 raw Image is a kernel payload; flashing it to boot_a
  would not constitute a valid repacked boot image.

**Practical v4 downloads (historical pre-reconstructor package):**
[one ZIP]({v4_zip['url']}) — {v4_zip['size_bytes']:,} bytes, SHA256
{v4_zip['github_sha256']}; [its separate SHA256SUMS]({v4_sum['url']}) —
{v4_sum['size_bytes']} bytes, SHA256 {v4_sum['github_sha256']}.
This ZIP is not a ready-to-flash OEM partition. The 57-release pre-v4
historical count remains a past snapshot; this separately regenerated
**pre-v5 report** includes the two v4 downloads, giving 58/252.

The older [GitHub catalog](github-release-catalog.json) was generated at
{old['generated_utc']} with **{old['release_count']} releases and
{old['asset_count']} assets**, before v3 appeared. This report queries GitHub
live and retains that older snapshot as historical evidence.

## Source archive is not a reproducible build

The {types['source-and-metadata-only']} old source tarballs and Git tags
preserve source checkpoints, and their GitHub SHA256 metadata makes the
downloaded tarballs identifiable. Neither existence of a snapshot nor a
filename containing tested proves that a matching, safe binary can be
rebuilt or booted. All **{len(rows)}** tag-to-commit relationships were
resolved against local annotated/lightweight Git refs. The independently
uploaded tar.gz contents have **not** been extracted and compared against
every Git tree, and all {summary["github_asset_count"]} asset payloads have **not** been rehashed
after download. Tag identity is not a device-test certificate.

The [HDD manifest](hdd-artifact-manifest.json) (captured
{manifest['generated_utc']}) records **{source_local} exact-tag release
folders** among the source-only releases with local Image, boot image,
config and Module.symvers. **{types['source-and-metadata-only']-source_local}**
source-only releases lack that exact four-file local set in the recorded
release directories. These files were never attached to those old GitHub
source-only releases. An unrelated top-level boot file or an experiments/
directory with a similar name is **not** silently attributed to a tag.
The manifest SHA256 values are hashes captured earlier, not fresh verification
of current HDD bytes and not evidence of an independent backup.

**Toolchain and build state:** the final hybrid stable local
REPRODUCE.txt records clang-r353983c and
aosp-aarch64-linux-android-4.9-android10 at kernel checkpoint
7124b9c09a48380a7b028104e17cac36b9b1a0af.
[The build helper](../../../tools/tbj606f/build-kernel.sh) requires
KERNEL_OUT, CLANG_DIR, CROSS_DIR and the Bengal defconfig/config fragment,
but does not bundle these toolchain binaries. The stable
[bring-up documentation](../android16-zui14-bringup.md) identifies
.config SHA256
36270e3c45eb9e663e71eef8579617f09ad25d7732d009d5d4c1ea96f55bf734
and Module.symvers SHA256
dc7acfa28137adf12a3d7fae68ed0c9fe80a71a675abeada5653cb6344b37b13,
which were separately reproduced for the **stable checkpoint**. That report
also explains that CONFIG_MODULE_SIG_ALL creates a local signing key:
source/config/ABI reproduction **does not imply byte-identical Image**.
The old 37 local config/ABI sets make later reconstruction more practical,
but this audit did not rebuild any of those historical tags or validate their
specific compiler binaries, signing keys, source-to-build mapping, boot
template, firmware or runtime logs.

## Deployment inventory and explicit cautions

GitHub has **{matches} release/asset digest records** whose SHA256 is found
in the older HDD manifest; this count includes identical v1 and v3 asset bytes
twice, not 20 unique independent backups. In particular, v1 and v3 have
identical published Image, Image.gz, kernel.config, Module.symvers, System.map,
p11_audio_compat.ko and TESTED-IMAGE-HASHES.txt SHA256. v1 and v3 publish
the tested kernel as separate assets; v4 bundles the kernel in its ZIP.
None distributes proprietary OEM boot/vendor images or the separate GSI.
For the final hybrid, the saved HDD folder
releases/p11-a16-zui14-hybrid-stable-20260924 contains:

- privately preserved boot-z14-adsp-loader-stable1.img:
  SHA256 93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635;
- privately preserved vendor_a-zui14-vndk30-z12wifi-z12audio-v5-760MiB.img:
  SHA256 b0cca3012109d045122dccdbd22f2505327ec7550576daa37d4bde643a39d3dd;
- REPRODUCE.txt plus the runtime identity, sensorservice, Wi-Fi, audio,
  camera and persistent boot captures. They document the validated **final
  Android 16/ZUI14 hybrid**, not blanket validation of every old milestone.

The separate LineageOS 23.2 Android 16 EROFS GSI remains on the Mac, reported
SHA256 26cde4242d9b92fb917b8235c4908e88c5fa6b60db1c56e0c53561db61d333bd.
**New direct source-to-stable-boot proof (post-v4):** original stock ZUI14
14.0.147 boot.img (SHA256
7356b6ac6a791c9508778aa76fe0fe381ca73eb225c7f10831799ed64f0e67d4)
has a different DTB/ramdisk and merely replacing its kernel does **not**
yield the validated boot. The new
[stable-boot reconstructor](../../../tools/tbj606f/reconstruct-stable-boot.py)
reconstructs the EXACT 14,286,848-byte stable boot SHA256
93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635
from the owner's original **ZUI12 12.0.519 QFIL boot.img** SHA256
d4e86ef850d4109a8b2b7a87bec82dd2c60cc68a6f0e3709e7bec0f74ff982d8
and public Image SHA256
af0b7b6b81c4f6ba3c5c2fbb044972a1bf502453ec19effa6d3664c094fdb2f8.
It checks inputs, retains the verified ZUI12 DTB, derives the EROFS ramdisk,
and checks exact finished boot SHA256. **The prior validated hybrid boot
backup is no longer required** when those original owner-supplied ZUI12
boot bytes and public Image are available. The old v4 ZIP was published
before the new reconstructor, and its notes still describe the previous
backup requirement; the post-v4 script must not be retrospectively claimed
as part of the historic two-asset v4 publication. This new exact boot proof
does not establish independent binary rebuilds for the 54 older source-only
kernel releases or remove the vendor/GSI prerequisites.

The owner must also obtain exact ZUI14 14.0.147 vendor input and ZUI12
12.0.519 Wi-Fi/audio modules legally, reconstruct the hybrid and keep a
restore path. The firmware requirements, tested-template hash checks, slot
and temporary-boot limitations are in [installation.md](../installation.md):
system_a/vendor_a may already have changed before boot_a passes a temporary
boot check. No archive release should be flashed merely because a matching
source snapshot or staged local boot file exists.

## Historically successful, partial, failed or reversed milestones

The explicitly **failed** GPU 980 MHz experiment is
zui12-post157-gpu-oc15-980-failed-20260922. The early 65 Hz panel probe was
later reverted by zui12-4.19.96-60hz-tested-20260917. The GPU oc16 harness,
the F2FS compression core-off build and the EROFS built milestone are build
checkpoints, **not independently proven successful runtime boots**. The
separate EROFS LZ4 decoder source release expressly disclaims a full-system
boot claim; the ADSP/sensor tag records a partial stage rather than the final
validated hybrid. The EROFS built, tested and runtime-tested release tags
point to **one same source commit**, as do the KGSL and modernization aliases.
Do not count them as independent successful builds or distinct codebases.

Historic tested tags with an HDD VALIDATION note have additional local
provenance, but those notes are not new tests and are not universally complete
Wi-Fi/audio/sensor/boot reports. The clearest final integrated success is
the v1/v3-shared kernel with the known-good ZUI14/ZUI12 hybrid and saved
2026-09-24 runtime capture: 34 sensors, audio policy, Wi-Fi and persistent
slot-A boot. v3 packages v1-identical kernel bytes and deployment helpers;
it does **not** claim a newly performed full flash or a distinct validated
kernel build. See [development-history.md](../development-history.md),
[android16-zui14-bringup.md](../android16-zui14-bringup.md), and the v1/v3
release notes for the stated scope.

"""
    insertion = introduction.strip().splitlines() + [""]
    lines[5:5] = insertion
    for row in rows:
        name=row["tag"]
        assetdesc=f"{row['class']} ({len(row['assets'])})"
        sha=t+row["source_tar_sha256"][:12]+t if row["source_tar_sha256"] else "—"
        hdd="local Image/boot/config/ABI" if row["hdd_exact_tag_complete_set"] else "no exact-tag complete set"
        lines.append(f"| [{t}{name}{t}]({row['release_url']}) | "
            f"[{t}{row['source_commit'][:10]}{t}]({row['source_commit_url']}) | "
            f"{assetdesc} | {sha} | {hdd} | {row['disposition']} |")
    lines.extend(["", "## Audit data", "",
        f"- {len(rows)} releases, {summary['github_asset_count']} assets, "
        f"{len(missing)} missing asset digests, {len(commit_aliases)} unique source commits.",
        f"- {types['source-and-metadata-only']} source-only releases: {source_local} exact-tag "
        f"local staged Image/boot/config/ABI sets, "
        f"{types['source-and-metadata-only']-source_local} without such a set.",
        f"- {matches} release/asset digest records match the previous HDD SHA manifest "
        "(duplicates across v1/v3 counted separately).",
        f"- Old catalog: {old['release_count']} releases / {old['asset_count']} assets at "
        f"{old['generated_utc']}, predating v3.",
        "", "Rebuild audit metadata with: "+t+"python3 tools/tbj606f/audit-releases.py"+t+".",
        "No firmware, flash device, deletion, or kernel build is performed. The post-v4 stable-boot reconstruction proof is reported from the validated reconstructor, not presented as a fresh device flash.",""])
    opts.markdown_output.write_text("\n".join(lines))
    print(json.dumps(summary,indent=2))
    print("alias groups:",out["source_commit_alias_groups"])

if __name__ == "__main__":
    main()
