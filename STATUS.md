# Current Status

## Android 16 / ZUI14 hybrid baseline

Validated on Lenovo Tab P11 TB-J606F Wi-Fi with LineageOS 23.2 Android 16
EROFS GSI and the ZUI14 14.0.147 hybrid vendor described in
Documentation/tbj606f/android16-zui14-bringup.md.

| Function | Status | Final validation |
|---|:---:|---|
| Boot / sys.boot_completed | Working | 1, persistent normal boot |
| EROFS root filesystem | Working | root mounted as EROFS |
| Touchscreen | Working | retained TB-J606F bring-up path |
| Sensors | Working | 34/34 hardware sensors enumerated |
| Automatic rotation | Working | Qualcomm Device Orientation used by WindowOrientationListener |
| Wi-Fi | Working | 5 GHz, 802.11ac |
| Audio | Working | Bengal sound card, AudioPolicyManager and primary speaker route |
| Bluetooth | Working | manager state ON |
| Camera | Working / enumerated | camera service reports two devices |
| Battery / AC reporting | Working | BatteryService values present |
| ZUI14 ADSP sensor path | Working | ADSP + FastRPC + sensor_pd up |

The stable kernel-code checkpoint is 7124b9c09. Later commits on the public
branch add source-only reproduction tools and documentation.

## Important compatibility choices

- ZUI14 userspace/vendor is retained where it works.
- Wi-Fi uses the ZUI12 qca_cld3_wlan.ko matching the kernel modversion ABI.
- Audio uses ZUI12 DLKMs matching the same ABI.
- The ZUI14 external ADSP loader is replaced by the in-kernel compatibility
  contract from 7124b9c09.
- Rouleur is not the TB-J606F codec path. The public audio compatibility module
  only satisfies two optional link-time references in the ZUI12 Bengal machine
  driver.
- Full ZUI14 modem/DSP replacement is not part of the stable configuration.

## Historical Linux Mobile status

The original project also targeted Linux Mobile/libhybris. That older status is
kept as historical context; the 2026 work documented here validates Android 16,
not a new Linux Mobile release.

## Safety / test policy

Use a device-scoped serial for every adb/fastboot command. Prefer temporary
fastboot boot for a new boot image before making it persistent. Do not wipe
userdata or resize the system partition as part of normal kernel iteration.
