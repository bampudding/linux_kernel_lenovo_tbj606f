# TB-J606F Android 16 / ZUI14 설치 ZIP

**지원 기기: Lenovo P11 TB-J606F Wi-Fi 전용.** 다른 P11 모델에 사용하지 마세요.
압축을 풀면 `install.sh`, 검증된 `Image`, 오디오 호환 모듈, boot/vendor 재구성
도구가 함께 있습니다. Git 또는 별도 커널 다운로드가 필요하지 않습니다.

## 준비물 (ZIP에 포함되지 않음)

- 언락된 TB-J606F, ADB 및 Fastboot 설치된 PC, USB 연결과 복구 가능한 원본 이미지.
- 본인 기기/백업에서 확보한 **검증된 ZUI12 DTB + EROFS ramdisk 기반 boot**.
  기준 SHA-256: `93f9e9518fc9a20691ab0b3579b0c628e23522674e827fc57b8867945aedd635`.
  순정 ZUI14 `boot.img`는 호환 템플릿이 아니며 그대로 사용하면 검증된 boot가 생성되지 않습니다.
- 해당 기기에 검증된 **ZUI14/ZUI12 hybrid `vendor.img`** 또는 Linux에서
  생성할 ZUI14 14.0.147 `vendor.img` + ZUI12 12.0.519 모듈 디렉터리.
- LineageOS 23.2 Android 16 EROFS GSI (2026-05-24 빌드).

원본 firmware, Qualcomm/Lenovo vendor, GSI 및 이미 구성된 hybrid vendor는
라이선스와 크기 때문에 이 ZIP에 포함되지 않습니다. 일반 사용자가 최초로 설치하려면 검증된 템플릿/복구 경로를 별도로 준비해야 합니다.
이 파일을 얻을 수 없는 상태에서 설치 성공을 보장하지 않습니다. 파일별 요구 SHA-256은
`installation.md`와 `TESTED-IMAGE-HASHES.txt`에 기록되어 있습니다.

## 1. ZIP 검증

ZIP 압축을 해제하고 이 폴더에서 실행하세요:

```sh
python3 verify-package.py
```

파일 하나라도 다르거나 빠져 있으면 설치하지 마세요.

## 2. PC에서 dry-run (Mac/Linux)

```sh
bash ./install.sh --offline --dry-run \
  --serial HA1E02DA \
  --gsi /path/to/LineageOS-23.2-20260524-GAPPS-EROFS-GSI.img \
  --stock-boot /path/to/your-validated-boot-template.img \
  --vendor-image /path/to/your-verified-hybrid-vendor.img
```

Linux에서 hybrid vendor를 직접 만들려면 `--vendor-image` 대신
`--zui14-vendor /path/to/zui14/vendor.img --zui12-modules /path/to/zui12/vendor/lib/modules`
옵션을 사용하세요. 전체 설명: `installation.md`.

## 3. 정상 검사 후 설치

위 명령에서 `--dry-run`만 제거하세요. 설치기는 기기/펌웨어/파일 해시,
fastboot 제품명, 언락 여부, partition 크기와 슬롯 A를 검사합니다.
`system_a`와 `vendor_a`를 설치한 다음 `fastboot boot`로 임시 부팅 검사에
성공해야 `boot_a`를 영구 플래시합니다. **임시 부팅이 실패하면 boot_a는
보존되지만 system/vendor는 이미 변경됐을 수 있으므로 복구 수단을 확보하세요.**
userdata 삭제/시스템 파티션 크기 변경은 수행하지 않습니다.

기존 GSI와 hybrid vendor가 이미 정확히 설치된 기기에서는
`--skip-system --skip-vendor`를 사용해 각각 재플래시를 건너뛸 수 있습니다.
이 옵션은 기존 내용의 정확한 이미지 해시까지 증명하지 않습니다.

## 검증된 커널 / source

Kernel Linux 4.19.157, source checkpoint `7124b9c09a48380a7b028104e17cac36b9b1a0af`.
Release source, full history, build helper and archive metadata:
https://github.com/bampudding/linux_kernel_lenovo_tbj606f

ZIP 자체는 소스 트리나 독점 플래시 이미지를 포함하지 않으며, 복제 가능한
GPL 소스는 위 저장소 태그에서 별도로 받으실 수 있습니다.
