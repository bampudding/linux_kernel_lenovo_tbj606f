// SPDX-License-Identifier: GPL-2.0-only
/*
 * Lenovo Tab P11 TB-J606F optional Rouleur link compatibility exports.
 *
 * The ZUI12 Bengal machine driver keeps link-time references to two Rouleur
 * helpers even on boards whose DT selects the WCD937x/Bolero codec path.
 * The TB-J606F uses that WCD937x/Bolero path, so the Rouleur callbacks are
 * never selected at runtime. Export inert helpers to let the ZUI12 machine
 * module load without requiring an ABI-incompatible Rouleur DLKM.
 */
#include <linux/module.h>

struct snd_info_entry;
struct snd_soc_component;
struct wcd_mbhc_config;

int rouleur_info_create_codec_entry(struct snd_info_entry *codec_root,
				    struct snd_soc_component *component)
{
	return 0;
}
EXPORT_SYMBOL(rouleur_info_create_codec_entry);

int rouleur_mbhc_hs_detect(struct snd_soc_component *component,
			   struct wcd_mbhc_config *mbhc_cfg)
{
	return 0;
}
EXPORT_SYMBOL(rouleur_mbhc_hs_detect);

MODULE_DESCRIPTION("Lenovo P11 optional Rouleur compatibility exports");
MODULE_LICENSE("GPL v2");
