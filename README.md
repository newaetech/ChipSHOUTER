# ChipSHOUTER®
ChipSHOUTER® - The Electromagnetic Fault Injection (EMFI) Platform By NewAE Technology Inc. This repo is used to hold the Python API, examples, and other useful information. Note some of these are held as submodules to allow you to grab specific content (such as the API) without needing to be totally overwhelmed with a bunch of PCB gerber files.

![](documentation/ChipSHOUTER_Example.jpg)

## Open-Source and Associated Tools

The full ChipSHOUTER is not OSHW, there are several repositories containing useful open-source tools that can be used with ChipSHOUTER and other EMFI platforms. These include:

* Ballistic Gel: a SRAM-based calibration board that can be used to measure the impact of EM (or other) fault injection. This is especially useful when comparing probe tip types.

* Simple EMFI Target: A very simple EMFI target, useful for quickly confirming an EMFI system is working. As it's completely stand-alone there is little risk of damaging connected devices, if you are trying things like spark-gap EMFI using a BBQ lighter.

* ChipShover is a XYZ table and controller. Note controller for this has fully open-source firmware, allowing you to develop unique extensions to the platform (nb: not yet released).

Parts of this repository have different licenses as noted in the files. The Python API is open-source for example under the MIT license.

## Documentation

Currently there is two main sources of documentation:

- [A PDF user manual](https://github.com/newaetech/ChipSHOUTER/raw/master/documentation/ChipSHOUTER%20User%20Manual.pdf) (includes serial command list).
- The [API documentation in HTML](https://chipshouter.readthedocs.io/en/latest/).

## What makes ChipSHOUTER® Awesome

ChipSHOUTER not only reduces the cost of EMFI research, it packages a complete learning environment. We include not only the injection tool, but different tips and target devices to help you understand the effects of EMFI. This includes a simple EMFI target to get you up and running, and the complex Ballistic Gel to help you understand what different injection waveforms and tip parameters mean for the resulting injected faults. 

## Buying a ChipSHOUTER®

ChipSHOUTER is currently available, see it on Mouser or in the [NewAE Store for Pre-order](http://store.newae.com/chipshouter-kit/).

## Disclaimers

Specifications are subject to change without notice. All product names are trademarks of their respective companies. ChipSHOUTER is a registered trademark of NewAE Technology Inc.

NewAE Technology Inc. makes no representations or warranties with respect to the accuracy or completeness of the contents of this documentation and reserves the right to make changes to specifications and product descriptions at any time without notice. NewAE Technology does not make any commitment to update the information contained herein. NewAE Technology products are not intended, authorized, or warranted for use as components in applications intended to support or sustain life. NewAE Technology products are designed solely for teaching purposes.