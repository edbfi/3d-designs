# Design notes

Where the dimensions came from, how the concept was chosen, and the measurements behind each decision.

## Sources

None of these files are in the repo. Radxa publishes them all on `dl.radxa.com`.

| What | Source | Used for |
|---|---|---|
| Armor Case 7056A | 2D drawings v1.00, one DXF per cover at 1:1 mm (`accessories/armor-case/hw/`) | Both covers' outlines, heights, fins, header recess, notches |
| Dragon Q6A | 3D STEP v1.21 and the 2D placement map (`dragon/q6a/hw/`) | Every connector's position and height |
| Header pinout | Radxa docs, *Dragon Q6A → Hardware use → Pin GPIO* | Pin 1 at the microSD end; the colour-coded header |
| AC019 FPC antenna | Radxa docs (Cubie A7Z antenna page) | 42 × 11.9 mm |
| NF-A8 5V PWM | Noctua's spec sheet | 80 × 80 × 25 mm, holes on 71.5 mm, cable 200 mm |

The case's x = 0 lines up with the board's, and the top cover's threaded holes sit on the board's 58 × 49 mm pattern, so case and board share one frame: x from the microSD end, y from the header edge.

## The case, from the drawings

| Feature | Value |
|---|---|
| Bottom cover | 85.0 × 56.0, R3 corners; 2.5 mm plate, 4.97 mm with the corner bosses the PCB rests on; notch at x 78.8–85, y 22.3–32.3 over the RTC connector J11 |
| Top cover | 69.29 × 56.0, 14.49 mm tall from the PCB top; it stops short of the USB/Ethernet block |
| Fins | 13 grooves 2.0 mm wide and 13 fins 1.4 mm wide, 3.4 mm pitch, running the full length and open at both ends; field y 6.9–51.1 |
| Header recess | x 6.13–58.93, 6.9 mm deep, open from above down to the PCB |
| Heights above the desk, case alone | PCB top 6.57, header pin tips 16.2, Ethernet top 20.2, fin tops 21.06, USB-A tops 22.8 |

Groove depth isn't on the drawings. Nothing here touches the fins, so it isn't needed.

## Board features the stand keeps clear

From the STEP (frame as above; z from the PCB top):

| Feature | x | y | Note |
|---|---|---|---|
| 40-pin header J20 | 7.17–57.97 | 0.15–7.36 | Pin tips +9.65; Dupont housings on it reach +16.5 |
| USB-C power | 6.69–15.63 | HDMI edge | The plug's overmould is about x 5.2–17.6 |
| HDMI | 24.55–39.55 | HDMI edge | |
| Audio jack | 50.87–57.17 | HDMI edge | Unused; the USB-end leg stands beside it |
| EDL button SW1 | 64.6–69.2 | HDMI edge | |
| microSD | underside, 0.6–11.85 | 21.8–33.1 | The card goes in at x = 0 |
| Power button SW2 | 0 | 34.6–39.2 | Pressed from the microSD end |
| Ethernet / USB-A | 67.0–88.3 | 2.0–18.3 / 21.1–36.7 / 39.6–55.3 | |
| RTC connector J11 | underside, 79.8–85.0 | 25.0–32.5 | Reached through the bottom cover's notch |
| Wi-Fi and BT antennas | 0 | about 10 and 29 | Their leads leave the case at the microSD end, with about 40 mm free |

The build checks every printed part against these as keep-out boxes (`keepouts()` in the source).

## Concept

Three council members (Claude Opus 5.5, GPT 6.1 Sol, Gemini 4 Argon) proposed concepts independently. The synthesis settled on:

- **Flat, pushing down onto the fins.** The grooves run lengthwise and are open at both ends, so air pushed down leaves along them at both ends. Pulling would lift air off the case through the hub's dead zone and draw back in warm air. Standing the case on edge leaves the header and HDMI sides fighting for the floor.
- **A gap under the fan instead of a duct.** Over a 13 mm gap, the air spreads past the motor hub before it reaches the fins.
- **Rubber-mounted fan and PETG parts.**

They differed on how to hold the fan:

| Concept | Why it won or lost |
|---|---|
| **Hood on legs plugged into a base under the case** (chosen) | Nothing touches the case's top. The hood comes off in one pull, for the header or the jumpers. Legs and base locate the case from below and at the corners, where no port is. |
| Clip frame gripping the top cover's sides | The sides carry the header and HDMI/USB-C. A clamp that stays clear of them grips too little aluminium, and there's nothing on the cover to clip into without modifying it. |
| Standoffs on the case's M2.5 screws | The screws go in from below into the top cover's legs, so only a part under the case can use them. It would also mean loosening the case's screws to fit the stand. |

## Layout decisions

| Decision | Value | Why |
|---|---|---|
| Fan position | Centred on the top cover (x 34.65) and its fin field (y 29.0) | Its bore then covers the whole cover length. The SoC pedestal (x 24.2–57.3, y 9.5–42.7) sits off-axis under the hub, but the gap spreads the air and the aluminium spreads the heat. |
| Fan gap | 13.0 mm, fin tops to fan | Jumper housings reach 16.5 mm above the PCB, 2 mm above the fin tops. The wires bend sideways above them, under the fan's overhang. |
| Legs | Outside the fan frame on both long sides, 1 mm clear of it; x −6.5…2.5 and 51.5…60.5 | The fan overhangs the 56 mm case by 12 mm a side, so legs over the case's corners would run through the fan's frame. These x positions keep clear of the USB-C plug's overmould and the EDL button. |
| Hold-down | None on the case's top | Ledges reaching 12 mm in from the legs would hang unsupported when printed. The case sits in the base's 2 mm lip, and the hood can't move once its legs are in their sockets. |
| Guard | Hub disc, rings at r 23.5 and 31, the bore's edge at 39, 8 spokes, 1.2 mm bars, 3 mm thick | Openings about 6.3 mm across, small enough to stop a fingertip reaching the blades. It's the first layers of the plate when printed, so it costs nothing. |
| Wi-Fi antennas | Upright sleeves 8.5 mm off the case's end, at y 1 and 55 | With about 40 mm of lead, they can't reach anywhere higher. Upright, in plastic and apart is better for RF than lying flat on the desk, and they lift with the unit. The sleeves stand outside the microSD slot, power button and most of the fin grooves. |
| Cable | A duct down the pin-1-end leg, ending in a holster | The fan's 5 V, GND, PWM and tach go to header pins 4, 6, 16 and 18, all within the first nine pin pairs at the microSD end. The duct hangs from an ear on the plate, so it prints without supports, and it holds the fan cable's spare length. |
| J11 | Floor and lip cut away under the notch | Leaves the RTC connector reachable from below and from the end. |

## Fits (PETG)

| Fit | Value | Fit-test sample |
|---|---|---|
| Case in the base | 0.2 mm per side, 2.0 mm lip (under the bottom cover's 2.5 mm plate top) | Frame |
| Leg in socket | 0.2 mm per side, with 0.35 mm crush ribs: 0.15 mm interference | Leg tip and socket |
| NA-AV1 | 4.6 mm hole, 1.5 mm web | Webs 1–5 try 1.2 / 1.5 / 1.8 mm webs and 4.3 / 5.0 mm holes |
| Antenna | 0.35 mm per side over 11.9 × 0.6 mm | Sleeve |
| Fan plug in the holster | 12.0 × 6.8 mm inside, 10 mm window to snap through | Duct bottom |

Noctua publishes no drawing of the NA-AV1. These values are first guesses until the fit test is printed.

## Material

The board idled at about 55 °C without a fan (measured in an earlier session). The aluminium case sits near that for hours, and the base and the hood's legs touch it or stand in its exhaust. PLA's heat deflection temperature is about 57 °C (Bambu PLA Basic), and it creeps under a steady load below that. PETG's is about 69 °C (Bambu PETG Basic). Every file is PETG. The air leaving the fins is barely warmer than the room: a few watts into the NF-A8's airflow warms it by about 0.4 °C (estimated).

## Thermal test

`/sys/class/thermal/`, all eight cores loaded for 5 minutes, sampled every 15 s, then 90 s of cooldown. "Max" is the hottest CPU or GPU zone.

| Run | Setup | Idle max | Loaded max | Skin | DDR | After 90 s |
|---|---|---|---|---|---|---|
| A | Fan loose on the case, USB, full speed | 45.9 °C | 64–70 °C | 40–42 °C | 48–50 °C | 27.8 °C |
| B | No fan | to do | | | | |
| C | Stand, USB, full speed | to do | | | | |
| D | Stand, wired to the header, under the overlay's fan curve | to do | | | | |

The stand passes if C is no worse than A. The CPU stayed at 2707 MHz throughout A, with no throttling.
