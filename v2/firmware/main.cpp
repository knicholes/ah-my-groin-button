/*
 * Ah! My Groin! v2 — button-triggered DY-SV17F audio playback
 *
 * On button press: wake from deep sleep, power up the DY-SV17F via
 * high-side P-MOSFET, pulse the IO0 trigger pin LOW, wait a fixed
 * playback window, power down DY-SV17F, sleep.
 *
 * Hardware:
 *  - HiLetgo Pro Mini 3.3V/8MHz (verify 8.000 MHz crystal!)
 *  - DY-SV17F audio module in I/O Independent Mode 0
 *    (CON1=GND via J8 pads 1-2, CON2=V33 via J9 pads 2-3, CON3 floats)
 *  - EG STARTS arcade button microswitch on D2 (INT0)
 *
 * Pin map:
 *  D2  INPUT_PULLUP  Button (LOW-level interrupt for wake)
 *  D5  OUTPUT        DY-SV17F power-gate (HIGH = powered)
 *  D6  OUTPUT        DY-SV17F IO0 trigger (LOW pulse = play 00001.mp3)
 *  D7  INPUT         DY-SV17F CON3 line — NO PULLUP. A pullup here pulls
 *                    CON3 HIGH during the module's boot mode-sample,
 *                    which selects the wrong mode and silences playback.
 *                    BUSY readout is therefore unavailable; playback
 *                    timing uses a fixed PLAY_DURATION_MS instead.
 */

#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/power.h>

#define BTN_PIN   2
#define GATE_PIN  5
#define TRIG_PIN  6
#define BUSY_PIN  7

#define BOOT_MS           50
#define TRIG_PULSE_MS    100
#define PLAY_DURATION_MS 4000

volatile bool buttonPressed = false;

void buttonISR() {
    detachInterrupt(digitalPinToInterrupt(BTN_PIN));
    buttonPressed = true;
}

void enterDeepSleep() {
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    attachInterrupt(digitalPinToInterrupt(BTN_PIN), buttonISR, LOW);
    sleep_cpu();
    sleep_disable();
}

void playAudio() {
    digitalWrite(GATE_PIN, HIGH);
    delay(BOOT_MS);

    digitalWrite(TRIG_PIN, LOW);
    delay(TRIG_PULSE_MS);
    digitalWrite(TRIG_PIN, HIGH);

    delay(PLAY_DURATION_MS);

    digitalWrite(GATE_PIN, LOW);
}

void setup() {
    pinMode(BTN_PIN, INPUT_PULLUP);
    pinMode(GATE_PIN, OUTPUT);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(BUSY_PIN, INPUT);

    digitalWrite(GATE_PIN, LOW);
    digitalWrite(TRIG_PIN, HIGH);

    power_adc_disable();
    power_spi_disable();
    power_twi_disable();
    power_timer1_disable();
    power_timer2_disable();

    for (int pin = 8; pin <= 13; pin++) pinMode(pin, INPUT_PULLUP);
    for (int pin = A0; pin <= A5; pin++) pinMode(pin, INPUT_PULLUP);
    ACSR |= (1 << ACD);

    enterDeepSleep();
}

void loop() {
    if (buttonPressed) {
        buttonPressed = false;
        delay(50);
        if (digitalRead(BTN_PIN) == LOW) {
            playAudio();
        }
        enterDeepSleep();
    }
}
