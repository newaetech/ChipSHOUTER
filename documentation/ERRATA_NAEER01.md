# NewAE Errata Note 01

**Product**: ChipSHOUTER

**Summary**: The output protection resistors can fail, giving a permanent "probe open" fault that does not clear.

**User Can Diagnose**: Yes

**User Can Fix or Workaround**: No

## Symptoms & Troubleshooting

The user will always see the "Open" LED on the enclosure light up.

Testing method:

1. Use different probe tips - the tips could have an internal open.
2. If Open light is still on, perform a "detection voltage" measurement to see if the output resistor is working correctly or is high resistance.

### Measuring Detection Voltage

To do this test, you will need a multimeter and a 1K-ohm resistor.

1. With the probe tip removed, measure the voltage at the output of the ChipSHOUTER SMA with the unit powered up. The negative lead goes to the SMA shield, and the positive leg goes to the SMA center pin. It should read around 15V (14V - 18V).
2. Using a 1K-ohm resistor, short the center pin of the SMA to the outside shield of the SMA. Measure the voltage at the center pin of the SMA again.
3. The center pin voltage with the 1K-ohm resistor should be 0.8V or higher (normally around 1V). Voltages lower than 0.5V indicate the output resistor may be damaged.

**Step 1 measurement shown here:**

<img src="images\ER01_ChipSHOUTER_TipMeas1.jpg">

**Step 2 measurement shown here:**

<img src="images\ER01_ChipSHOUTER_TipMeas1KRes.jpg">

## Repair

The repair involves replacing the resistor. This cannot be performed at the user site as the ChipSHOUTER high voltage portions of the board have a 2-stage coating that requires a heat cure. The repair involves removing the coating, replacing the part, and replacing the coating.

The repaired units (as well as newly built units) use a different part with improved pulse power ratings.

## Notes

The two output resistors are designed such the high-side resistor will fail first, and serves as a "last resort fuse" designed to protect the more difficult to repair portions. Due to component availability issues a substitution was made on the resistor when the ChipSHOUTERs were first produced, and that substitution has continued in all production units. When the substitution was selected, it had more limited manufacture provided pulse power ratings than our desired part, but testing showed it seems to work OK with a sufficiently happy margin.

The problem appears more prevalent in a later date code for these specific resistors, suggesting the initial validation may have been done on what happened to be a "better" batch. ChipSHOUTERs with the issue have all had resistor datecode `2027` (this will not be visible until the unit is opened and parts of the coating removed).

All repaired units & all new units use a part from another manufacture & product family that is fully specified at our pulse widths & power levels. This was the *originally specified part* from our design, which at the time was unavailable. We have now horded these resistors to ensure we don't need to substitute them in the future.