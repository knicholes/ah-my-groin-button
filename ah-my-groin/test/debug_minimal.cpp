#include <Arduino.h>

// Minimal hardware test - no complex classes
#define BUTTON_PIN 2
#define DFPLAYER_ENABLE_PIN 5

volatile bool buttonPressed = false;

void buttonISR() {
    buttonPressed = true;
}

void setup() {
    Serial.begin(9600);
    delay(2000); // Wait for serial connection
    
    Serial.println(F("=== MINIMAL HARDWARE DEBUG TEST ==="));
    Serial.println(F("Testing basic button and serial communication"));
    
    // Setup button
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);
    
    // Setup DFPlayer enable pin
    pinMode(DFPLAYER_ENABLE_PIN, OUTPUT);
    digitalWrite(DFPLAYER_ENABLE_PIN, LOW); // Start disabled
    
    Serial.println(F("Hardware initialized"));
    Serial.println(F("Press button to test..."));
}

void loop() {
    if (buttonPressed) {
        buttonPressed = false;
        
        Serial.println(F("BUTTON PRESSED!"));
        
        // Toggle DFPlayer enable pin as visual test
        digitalWrite(DFPLAYER_ENABLE_PIN, HIGH);
        delay(500);
        digitalWrite(DFPLAYER_ENABLE_PIN, LOW);
        
        Serial.println(F("Button test complete"));
    }
    
    delay(100);
} 