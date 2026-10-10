# Seven unmatched legacy builds — source attribution and preservation

All seven archived original `Image` SHA256 values were independently rehashed and checked against the earlier historical build map. The seven corresponding `Image`, `.config`, `Module.symvers` and `vmlinux` archives were uploaded and their remote GitHub SHA256 and size verified. **No fresh byte-identical rebuild has been demonstrated.**

| Historical build folder | Source branch / decision | Limitation |
|---|---|---|
| `lineage4132-zui14config-abi-probe` | [archive/lineage4132-zui14config-abi-probe-20260923](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/archive/lineage4132-zui14config-abi-probe-20260923) | Source snapshot was already a separate local git repository; new remote archival branch. No clean rebuild performed. |
| `p11diag-recovery-lz4-v15` | [p11/diag-recovery-permissive](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/p11/diag-recovery-permissive) | Historical reflog records this branch immediately before build; original worktree now absent. |
| `zui12-post157-erofs-lineage23.2-final` | [p11/zui12-post157-erofs-lineage23.2](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/p11/zui12-post157-erofs-lineage23.2) | Branch commit before Image completion, but compile.h predates commit; incremental stale objects possible. |
| `zui12-post157-erofs-z14-adsp-loader1` | [p11/zui12-post157-erofs-z14-glink1](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/p11/zui12-post157-erofs-z14-glink1) | Build immediately after glink1 commit; later stable ADSP commit 7124b9c is too late to be this build. |
| `zui12-post157-erofs-z14-fastrpc-backport-test` | [p11/zui12-post157-erofs-z14-adsp-loader-stable](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/p11/zui12-post157-erofs-z14-adsp-loader-stable) | Image hash also equals public-v1 and public-v3 Image; later fastrpc experiment commit too late. |
| `zui12-post157-erofs-z14-fastrpc-clean` | [p11/zui12-post157-erofs-z14-fastrpc-experiment](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/tree/p11/zui12-post157-erofs-z14-fastrpc-experiment) | Image follows fastrpc experiment commit; source context only, no clean rebuild. |
| `zui12-source-zui14config-abi-probe` | Release only; no defensible source commit | Build predates erofs lineage23.2 commit, source was an intermediate/uncommitted state; unique config, conflicting stale CLANG_VERSION in .config.old. No defensible exact commit. |

Download the exact saved output from the [historical build-output release](https://github.com/bampudding/linux_kernel_lenovo_tbj606f/releases/tag/tbj606f-legacy-gpl-build-outputs-20260925). Each archive has `BUILD-PROVENANCE.json` and the output hashes are indexed in [machine-readable seven-build inventory](seven-unmatched-build-resolution-20260925.json). Source branches are **contextual candidates** supported by original source path, commit/reflog timing and build evidence, not proof that checking out the branch alone yields identical bytes.

The newly published `archive/lineage4132-zui14config-abi-probe-20260923` branch is the original standalone 2026-09-23 source repository commit `d182dbf6176d947d1241c977f4135c6641309b09`, not an invented cherry-pick on the ZUI12 source. The other five source branches were already on GitHub; redundant alias branches were deliberately avoided. The final `zui12-source-zui14config-abi-probe` has only its original binary/config archive until its uncommitted source state can be proven.

The current stable public-v5 flash-kit release and current performance source/build environment were not changed. No original HDD build was deleted.
