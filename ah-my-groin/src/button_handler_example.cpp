/*
 * ButtonHandler Usage Example
 * 
 * Demonstrates how to use the ButtonHandler class for button-triggered audio device.
 * This example shows the integration with the main audio system.
 */

#include <Arduino.h>
#include "ButtonHandler.h"

// Example usage of ButtonHandler
void setup() {
    Serial.begin(9600);
    Serial.println(F("ButtonHandler Example Starting..."));
    
    // Initialize button handler
    buttonHandler.begin();
    
    Serial.println(F("Button handler initialized"));
    Serial.println(F("Press the button to test functionality"));
}

void loop() {
    // Update button state (should be called regularly)
    buttonHandler.update();
    
    // Check for button press
    if (buttonHandler.wasPressed()) {
        Serial.println(F("Button was pressed!"));
        Serial.print(F("Press count: "));
        Serial.println(buttonHandler.getPressCount());
        Serial.print(F("Press time: "));
        Serial.println(buttonHandler.getLastPressTime());
        
        // This is where audio playback would be triggered
        // playAudio();
    }
    
    // Check for button release
    if (buttonHandler.wasReleased()) {
        Serial.println(F("Button was released"));
        Serial.print(F("Release time: "));
        Serial.println(buttonHandler.getLastReleaseTime());
    }
    
    // Check current button state
    static bool lastPrintedState = false;
    bool currentState = buttonHandler.isPressed();
    if (currentState != lastPrintedState) {
        Serial.print(F("Button state: "));
        Serial.println(currentState ? "PRESSED" : "RELEASED");
        lastPrintedState = currentState;
    }
    
    // Small delay to prevent overwhelming serial output
    delay(10);
}