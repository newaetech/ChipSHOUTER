# ChipSHOUTER Firmware Update

## Downloading Firmware Update File

The firmware update file is downloaded from the following URL: https://media.newae.com/cw520fw/all_devices/cw520_XXXXXX_2-0-3_firmware.fup

You need to replace XXXXXX with the board id.

### Updating Firmware

If your ChipSHOUTER is already programmed, connect and run the `update_firmware()` function to reprogram your device:

```python
from chipshouter import ChipSHOUTER
cs = ChipSHOUTER('<SERIAL_PORT>')
cs.update_firmware('/path/to/firmware.fup')
```

If your ChipSHOUTER is in bootloader mode (it's printing out its board id over the serial port), run the following to reprogram:

```python
from chipshouter import ChipSHOUTER
ChipSHOUTER.update_firmware(None, "/path/to/firmware.fup", comport="<SERIAL_PORT>")
```

Documentation for the `update_firmware()` function can be found here: https://chipshouter.readthedocs.io/en/latest/#chipshouter.chipshouter.ChipSHOUTER.update_firmware

## Firmware Update Releases

### 2.0.3
Fix temperature sensor lockup when read during glitching. Should make trigger_safe unnecessary

### 2.0.2
Fix occasional lockup which causes device reset

### 2.0.1
Change trigger_safe behaviour
