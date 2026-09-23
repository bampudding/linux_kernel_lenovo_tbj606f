// SPDX-License-Identifier: GPL-2.0-only
/*
 * Minimal ADSP loader for Lenovo P11 / Bengal ZUI14 vendor userspace.
 *
 * ZUI14 normally supplies this functionality from audio_adsp_loader.ko.
 * The stock prebuilt module is not modversion-compatible with this kernel,
 * so provide the small kernel-side contract that vendor init actually uses:
 * /sys/kernel/boot_adsp/{boot,ssr} and subsystem_get("adsp").
 */
#include <linux/device.h>
#include <linux/err.h>
#include <linux/kobject.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/sysfs.h>

#include <soc/qcom/subsystem_restart.h>

struct p11_adsp_loader {
	struct device *dev;
	void *pil_h;
	struct kobject *kobj;
	struct mutex lock;
};

static struct p11_adsp_loader *adsp_loader;

static ssize_t boot_store(struct kobject *kobj, struct kobj_attribute *attr,
			  const char *buf, size_t count)
{
	struct p11_adsp_loader *loader = adsp_loader;
	int value;
	int ret;

	if (!loader)
		return -ENODEV;

	ret = kstrtoint(buf, 10, &value);
	if (ret)
		return ret;
	if (value != 0 && value != 1)
		return -EINVAL;

	mutex_lock(&loader->lock);
	if (value == 1) {
		if (!loader->pil_h) {
			loader->pil_h = subsystem_get("adsp");
			if (IS_ERR(loader->pil_h)) {
				ret = PTR_ERR(loader->pil_h);
				loader->pil_h = NULL;
				dev_err(loader->dev,
					"failed to power up ADSP: %d\n", ret);
				mutex_unlock(&loader->lock);
				return ret;
			}
			dev_info(loader->dev, "ADSP powered up\n");
		}
	} else if (loader->pil_h) {
		subsystem_put(loader->pil_h);
		loader->pil_h = NULL;
		dev_info(loader->dev, "ADSP powered down\n");
	}
	mutex_unlock(&loader->lock);

	return count;
}

static ssize_t ssr_store(struct kobject *kobj, struct kobj_attribute *attr,
			 const char *buf, size_t count)
{
	struct p11_adsp_loader *loader = adsp_loader;
	int value;
	int ret;

	if (!loader)
		return -ENODEV;

	ret = kstrtoint(buf, 10, &value);
	if (ret)
		return ret;
	if (value != 1)
		return -EINVAL;

	mutex_lock(&loader->lock);
	if (!loader->pil_h) {
		mutex_unlock(&loader->lock);
		return -ENODEV;
	}
	ret = subsystem_restart_dev((struct subsys_device *)loader->pil_h);
	mutex_unlock(&loader->lock);
	if (ret)
		return ret;

	return count;
}

static struct kobj_attribute boot_attr = __ATTR(boot, 0220, NULL, boot_store);
static struct kobj_attribute ssr_attr = __ATTR(ssr, 0220, NULL, ssr_store);

static struct attribute *adsp_attrs[] = {
	&boot_attr.attr,
	&ssr_attr.attr,
	NULL,
};

static const struct attribute_group adsp_attr_group = {
	.attrs = adsp_attrs,
};

static int p11_adsp_loader_probe(struct platform_device *pdev)
{
	struct p11_adsp_loader *loader;
	int ret;

	if (adsp_loader)
		return -EBUSY;

	loader = devm_kzalloc(&pdev->dev, sizeof(*loader), GFP_KERNEL);
	if (!loader)
		return -ENOMEM;

	loader->dev = &pdev->dev;
	mutex_init(&loader->lock);
	loader->kobj = kobject_create_and_add("boot_adsp", kernel_kobj);
	if (!loader->kobj)
		return -ENOMEM;

	ret = sysfs_create_group(loader->kobj, &adsp_attr_group);
	if (ret) {
		kobject_put(loader->kobj);
		return ret;
	}

	platform_set_drvdata(pdev, loader);
	adsp_loader = loader;
	dev_info(&pdev->dev,
		 "registered ZUI14-compatible ADSP loader sysfs contract\n");
	return 0;
}

static int p11_adsp_loader_remove(struct platform_device *pdev)
{
	struct p11_adsp_loader *loader = platform_get_drvdata(pdev);

	if (!loader)
		return 0;

	mutex_lock(&loader->lock);
	if (loader->pil_h) {
		subsystem_put(loader->pil_h);
		loader->pil_h = NULL;
	}
	mutex_unlock(&loader->lock);

	adsp_loader = NULL;
	sysfs_remove_group(loader->kobj, &adsp_attr_group);
	kobject_put(loader->kobj);
	return 0;
}

static const struct of_device_id p11_adsp_loader_match[] = {
	{ .compatible = "qcom,adsp-loader" },
	{ }
};
MODULE_DEVICE_TABLE(of, p11_adsp_loader_match);

static struct platform_driver p11_adsp_loader_driver = {
	.probe = p11_adsp_loader_probe,
	.remove = p11_adsp_loader_remove,
	.driver = {
		.name = "p11-zui14-adsp-loader",
		.of_match_table = p11_adsp_loader_match,
		.suppress_bind_attrs = true,
	},
};

builtin_platform_driver(p11_adsp_loader_driver);
