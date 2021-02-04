# NewAE Errata Note 02

**Product**: ChipSHOUTER

**Summary**: Firmware before 1.8.7 wrote every change to EEPROM, causing rapid EEPROM wear on one page.

**User Can Diagnose**: Yes

**User Can Fix or Workaround**: Yes

## Symptoms & Troubleshooting

The most common symptoms are:

1. Device does not boot, and prints only the BOARD-ID out the serial console.
2. Device boots, but reports a CRC error.
3. Device boots, but has a constant "latched" error (faults status can be stored in EEPROM, and invalid fault data is loaded).

Very occasionally the error causes devices to not accept new firmware upgrades - this requires a hardware replacement.

## Repair

Firmware 1.8.7 and onward do not have this problem. The affected EEPROM page is mapped out of use in this firmware and onward, so no physical replacement is required to restore full reliability to existing units.

### Work-Around

Upgrading to the latest firmware does not require a work-around. If you need to run an older firmware, run your scripts to minimize changes to settings (for example - do not change voltage every time).

## Notes

The ChipSHOUTER uses an Atmel XMEGA - this device has internal EEPROM with about 100K cycle write/erase.

On firmware before 1.8.7, every change (such as voltage or pulse width) is written to EEPROM, and becomes the new power-on default. Running a script for example which selects a new random voltage every second would kill the EEPROM page in only 28 hours of usage.

Firmware 1.8.7 and onward require the user to explicitly cause an EEPROM write.

The bootloader uses part of the EEPROM page as a flag to indicate the device status, and if a flag is set the device stays in the bootloader. This byte is part of the same page used by the general settings - it's possible (but rare) for this flag to get "stuck" and forces the device into bootloader mode every time.

This failure mode requires a physical replacement, as the bootloader will never allow the firmware to boot successfully. This flag isn't normally needed, so firmware 1.8.7 and onward do not touch the old flag location either to ensure no future failures occur.