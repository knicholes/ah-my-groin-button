/*
 * "Ah! My Groin!" Button-Triggered Audio Device
 * 
 * A battery-efficient Arduino-based device that plays audio when a button is pressed.
 * Features ultra-low power consumption using deep sleep mode.
 * 
 * Hardware Requirements:
 * - Arduino Pro Mini 3.3V/8MHz (with power LED removed)
 * - DFPlayer Mini MP3 module
 * - Large momentary pushbutton
 * - 8Ω 2-3W speaker
 * - MicroSD card with audio file
 * - 3x AA batteries (4.5V total)
 * 
 * Power Consumption:
 * - Deep sleep: ≤10µA
 * - Active (playing): ~150mA
 * - Expected battery life: 6-18 months depending on usage
 */

#include <Arduino.h>
#include <SoftwareSerial.h>
#include "PowerManager.h"
#include "ButtonHandler.h"
#include "AudioController.h"
#include "SystemController.h"

// Pin definitions
#define DFPLAYER_RX 3   // Arduino Pin 3 -> DFPlayer RX
#define DFPLAYER_TX 4   // Arduino Pin 4 -> DFPlayer TX
#define DFPLAYER_ENABLE 5  // Arduino Pin 5 -> DFPlayer Enable
#define BUTTON_PIN 2    // Button input (INT0 for wake-up)

// Create software serial for DFPlayer communication
SoftwareSerial dfPlayerSerial(DFPLAYER_TX, DFPLAYER_RX);

// Create AudioController object
AudioController audioController(dfPlayerSerial, 15);

// Create integrated SystemController
SystemController systemController(powerManager, audioController, buttonHandler);

// Forward declarations
void handleButtonPress();

void setup() {
  #ifdef DEBUG
  Serial.begin(9600);
  Serial.println(F("Button-Triggered Audio Device Starting..."));
  Serial.println(F("Integrated Power Management System Initializing..."));
  #endif
  
  // Initialize PowerManager with pin assignments
  powerManager.begin();
  
  // Initialize ButtonHandler with interrupt-based input
  buttonHandler.begin();
  
  // Initialize DFPlayer serial communication
  dfPlayerSerial.begin(9600);
  
  // Initialize integrated SystemController
  if (!systemController.begin()) {
    #ifdef DEBUG
    Serial.println(F("SystemController initialization failed!"));
    Serial.flush();
    #endif
    // Continue anyway - system may still work with degraded functionality
  }
  
  #ifdef DEBUG
  Serial.println(F("Integrated system initialized - entering deep sleep"));
  Serial.flush();
  #endif
  
  // Enter deep sleep immediately after setup using integrated controller
  // Device will wake on button press
  delay(100);
  systemController.enterSleepMode();
}

void loop() {
  // This should rarely execute due to deep sleep mode
  // Main execution happens in interrupt-driven button handling
  
  // Update button state
  buttonHandler.update();
  
  // Check for button press using integrated SystemController
  if (buttonHandler.wasPressed()) {
    handleButtonPress();
  }
  
  // Return to deep sleep using integrated controller
  delay(100);
  systemController.enterSleepMode();
}

void handleButtonPress() {
  #ifdef DEBUG
  Serial.println(F("Button pressed - using integrated system controller"));
  Serial.print(F("Press count: "));
  Serial.println(buttonHandler.getPressCount());
  #endif
  
  // Use integrated SystemController for coordinated power management and audio playback
  systemController.handleButtonPress();
  
  // Check for any system errors and report them
  if (systemController.hasError()) {
    #ifdef DEBUG
    Serial.print(F("SystemController error: "));
    Serial.println(systemController.getLastError());
    #endif
    
    // Clear error for next operation
    systemController.clearError();
  }
  
  #ifdef DEBUG
  Serial.print(F("Operation completed in "));
  Serial.print(systemController.getTotalOperationTime());
  Serial.println(F("ms"));
  Serial.flush();
  #endif
}

// Button interrupt handling is now managed by ButtonHandler class
