# Current Status

## Tested configuration

| Item | Tested baseline |
|---|---|
| Device | Lenovo Tab P11 TB-J606F Wi-Fi |
| SoC | Qualcomm Bengal |
| Kernel | Linux 4.19.157-perf+ |
| Android | LineageOS 23.2 / Android 16 EROFS GSI |
| Vendor userspace | Lenovo ZUI14 14.0.147 |
| Stable kernel checkpoint | `7124b9c09` |
| Public integration branch | `opensource/tbj606f-a16-zui14` |

## Hardware status

| Function | Android 16 hybrid | Notes |
|---|:---:|---|
| Boot | ✓ | `sys.boot_completed=1` |
| EROFS root | ✓ | compressed Android 16 system/root tested |
| Touchscreen | ✓ | NT36523W/nt36xxxspi |
| Double-tap wake | ✓ | GSI-safe panel PM handling |
| Wi-Fi | ✓ | ZUI12 ABI-compatible WLAN module; 5 GHz/11ac tested |
| Bluetooth | ✓ | controller/service enabled |
| Sensors | ✓ | 34 hardware sensors enumerated |
| Auto rotation | ✓ | Qualcomm Device Orientation sensor used |
| Sound | ✓ | Bengal machine driver + WCD937x/Bolero path |
| Cameras | ✓ | two camera devices enumerated |
| Battery/charging | ✓ | AC/charge/battery properties reported |
| GPU | ✓ | guarded 960 MHz opt-in work retained in history |
| Suspend/resume | partial | normal Android suspend/resume works; continue long-duration stress testing |
| GPS | n/a | TB-J606F Wi-Fi model |

## Android 16 / ZUI14 compatibility notes

The working configuration is intentionally hybrid rather than a blind ZUI14
firmware transplant.

- ZUI14 userspace and vendor HALs are retained.
- The kernel keeps the stable ZUI12-compatible ABI.
- A native kernel ADSP loader provides the ZUI14 `/sys/kernel/boot_adsp`
  userspace contract.
- Wi-Fi uses the ZUI12 module that matches the preserved kernel modversion ABI.
- Audio uses ZUI12-compatible DLKMs.
- The optional Rouleur compatibility shim only satisfies two link-time symbols
  needed by the Bengal machine module; TB-J606F actually selects the
  WCD937x/Bolero codec path.
- Full ZUI14 modem/DSP replacement is not required for the validated baseline.

## Development history

The full successful path and intentionally retained failed experiments are
documented in:

- `Documentation/tbj606f/development-history.md`
- `Documentation/tbj606f/android16-zui14-bringup.md`

Linux stable updates are kept as individual upstream commits, and device fixes
are kept as separate commits instead of being flattened into a source dump.
