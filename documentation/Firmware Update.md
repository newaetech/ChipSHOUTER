# ChipSHOUTER Firmware Update

## Downloading Firmware Update File

The firmware update file is downloaded from the following URL: https://media.newae.com/cw520fw/all_devices/cw520_XXXXXX_2-0-3_firmware.fup

You need to replace XXXXXX with the board id.

You can perform the firmware update with the `update_firmware()` function: https://chipshouter.readthedocs.io/en/latest/#chipshouter.chipshouter.ChipSHOUTER.update_firmware

## Firmware Update Releases

### 2.0.3
Fix temperature sensor lockup when read during glitching. Should make trigger_safe unnecessary

### 2.0.2
Fix occasional lockup which causes device reset

### 2.0.1
Change trigger_safe behaviour
