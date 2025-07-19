/*
 * ButtonHandler Compilation Test
 * 
 * Simple test to verify ButtonHandler compiles without errors
 */

#include <Arduino.h>
#include "../src/ButtonHandler.h"

void setup() {
    Serial.begin(9600);
    
    // Test ButtonHandler instantiation
    ButtonHandler testHandler(2, 50);
    testHandler.begin();
    
    // Test basic methods
    bool pressed = testHandler.isPressed();
    bool wasPressed = testHandler.wasPressed();
    bool wasReleased = testHandler.wasReleased();
    bool stateChanged = testHandler.stateChanged();
    
    // Test configuration methods
    testHandler.setDebounceDelay(100);
    unsigned long delay = testHandler.getDebounceDelay();
    
    // Test timing methods
    unsigned long pressTime = testHandler.getLastPressTime();
    unsigned long releaseTime = testHandler.getLastReleaseTime();
    unsigned long pressCount = testHandler.getPressCount();
    
    // Test control methods
    testHandler.update();
    testHandler.reset();
    testHandler.setupInterrupt();
    testHandler.enableInterrupt();
    testHandler.disableInterrupt();
    
    Serial.println("ButtonHandler compilation test passed!");
}

void loop() {
    // Test global instance
    buttonHandler.update();
    
    if (buttonHandler.wasPressed()) {
        Serial.println("Button pressed!");
    }
    
    delay(100);
}