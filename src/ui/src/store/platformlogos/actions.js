/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/

import microchipLogo from "assets/images/microchip-logo.png";
import espressifLogo from "assets/images/espressif-logo.png";
import armLogo from "assets/images/arm-logo.png";
import arduinoLogo from "assets/images/arduino-logo.png";
import efablessLogo from "assets/images/efabless-logo.png";
import infineonLogo from "assets/images/infineon-logo.png";
import m5stackLogo from "assets/images/m5stack-logo.png";
import nordicSemiconductorLogo from "assets/images/nordic-semiconductor-logo.png";
import nxpLogo from "assets/images/nxp-logo.png";
import onsemiLogo from "assets/images/onsemi-logo.png";
import quicklogicLogo from "assets/images/quicklogic-logo.png";
import raspberrypiLogo from "assets/images/raspberry-pi-logo.png";
import siliconLabsLogo from "assets/images/silicon-labs-logo.png";
import stmicroLogo from "assets/images/stmicro-logo.png";
import x86GCCLogo from "assets/images/x86-gcc-logo.png";
import minGWLogo from "assets/images/windows-x86-logo.png";
import androidLogo from "assets/images/android-logo.png";

import { SET_PLATFORM_LOGOS } from "./actionTypes";

export const loadPlatformLogos = () => {
  return {
    type: SET_PLATFORM_LOGOS,
    payload: {
      Microchip: microchipLogo,
      Espressif: espressifLogo,
      ARM: armLogo,
      Arduino: arduinoLogo,
      Infineon: infineonLogo,
      M5Stack: m5stackLogo,
      "Nordic Semiconductor": nordicSemiconductorLogo,
      NXP: nxpLogo,
      onsemi: onsemiLogo,
      QuickLogic: quicklogicLogo,
      "Raspberry Pi Foundation": raspberrypiLogo,
      "Silicon Labs": siliconLabsLogo,
      STMicroelectronics: stmicroLogo,
      "x86 GCC": x86GCCLogo,
      MinGW: minGWLogo,
      Google: androidLogo,
      eFabless: efablessLogo,
    },
  };
};
