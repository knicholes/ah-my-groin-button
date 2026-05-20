// DIAGNOSTIC FIRMWARE — TEMPORARY (real firmware in main.cpp.bak)
//
// Holds D5 HIGH continuously to force the DY-SV17F power chain ON.
// No button, no sleep, no timeout. Stay this way until reflashed.
//
// Measure (DC volts, black probe on GND):
//   J4 pad 8     (D5/GATE_CTRL)   should be ~3.3 V
//   Q4 collector (Q1_GATE)        should be ~0 V    (Q4 saturated -> pulls Q1 gate down)
//   Q1 drain     (VDFP test pt)   should be ~4.5 V  (Q1 ON, full battery voltage)
//   DY-SV17F V5  (left pin 6)     should be ~4.5 V  (via the flying wire)
//
// If D5 = 3.3V but Q4 collector NOT 0V  -> Q4 dead or bad solder joint
// If Q4 collector = 0V but Q1 drain NOT 4.5V  -> Q1 dead (likely smoke #2 victim)
// If Q1 drain = 4.5V but DY-SV17F V5 NOT 4.5V  -> V5 flying wire broken
// If everything reads correctly but module LED still dark  -> DY-SV17F dead

#include <Arduino.h>

void setup() {
    pinMode(5, OUTPUT);
    digitalWrite(5, HIGH);
}

void loop() {}
