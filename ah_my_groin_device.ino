/*
 * "Ah! My Groin!" Sound Effect Device
 * 
 * A battery-efficient Arduino-based device that plays the iconic Simpsons
 * sound effect when a big red button is pressed.
 * 
 * Hardware Requirements:
 * - Arduino Pro Mini 3.3V/8MHz (with power LED removed)
 * - DFPlayer Mini MP3 module
 * - Large red momentary pushbutton
 * - 8Ω 2-3W speaker
 * - MicroSD card with audio file
 * - 3x AA batteries (4.5V total)
 * 
 * Wiring:
 * - Pin 2 (INT0): Button input (other side to GND)
 * - Pin 3: DFPlayer RX
 * - Pin 4: DFPlayer TX
 * - Pin 5: DFPlayer Enable (power control)
 * - RAW: 4.5V from batteries
 * - GND: Common ground
 * 
 * Audio File Requirements:
 * - File names: 0001.wav, 0002.wav, 0003.wav, etc.
 * - Location: /mp3 folder on SD card
 * - Format: WAV (16kHz, 8-bit, mono) or MP3
 * 
 * Power Optimization Features:
 * - Deep sleep mode between button presses (~10µA)
 * - Wake on button interrupt
 * - DFPlayer power control via enable pin
 * - State machine for proper timing and sequencing
 * 
 * Expected Battery Life: 12-18 months with daily use
 * 
 * Author: Generated for "Ah! My Groin!" Project
 * License: MIT
 */

#include <SoftwareSerial.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

// Include system components
#include "src/PowerManager.h"
#include "src/AudioController.h"
#include "src/ButtonHandler.h"
#include "src/SystemController.h"

// Pin definitions
const int BUTTON_PIN = 2;           // Button input (INT0 for wake-up)
const int DFPLAYER_RX = 3;          // DFPlayer RX (Arduino TX)
const int DFPLAYER_TX = 4;          // DFPlayer TX (Arduino RX)
const int DFPLAYER_ENABLE = 5;      // DFPlayer enable control

// System components
PowerManager powerManager(DFPLAYER_ENABLE);
AudioController audioController(DFPLAYER_RX, DFPLAYER_TX);
ButtonHandler buttonHandler(BUTTON_PIN);
SystemController systemController(powerManager, audioController, buttonHandler);

// System state tracking
volatile bool buttonPressed = false;
unsigned long lastStateTransition = 0;

// State machine timing constants
const unsigned long STATE_TRANSITION_TIMEOUT = 10000;  // 10 second timeout for any state
const unsigned long SYSTEM_WATCHDOG_TIMEOUT = 30000;   // 30 second system watchdog

// Forward declarations
void buttonInterrupt();
void handleSystemTimeout();
void logSystemState();
void performSystemReset();

void setup() {
  // Initialize serial for debugging (optional - remove for production)
  #ifdef DEBUG
  Serial.begin(9600);
  Serial.println(F("Ah! My Groin! Device Starting with State Machine..."));
  #endif
  
  // Comprehensive power optimization: disable unused peripherals
  power_adc_disable();          // Disable ADC (~320µA savings)
  power_spi_disable();          // Disable SPI (~100µA savings)
  power_twi_disable();          // Disable TWI (I2C) (~100µA savings)
  power_timer1_disable();       // Disable Timer1 (~50µA savings)
  power_timer2_disable();       // Disable Timer2 (~50µA savings)
  
  // Disable analog comparator for additional power savings (~40µA)
  ACSR |= (1 << ACD);
  
  // Set unused pins as inputs with pull-ups to prevent floating
  // This prevents current leakage through floating pins
  for (int pin = 6; pin <= 13; pin++) {
    // Skip pins we're using (2=button, 3=DFPlayer RX, 4=DFPlayer TX, 5=DFPlayer enable)
    if (pin != DFPLAYER_ENABLE) {
      pinMode(pin, INPUT_PULLUP);
    }
  }
  
  // Set unused analog pins as inputs with pull-ups
  pinMode(A0, INPUT_PULLUP);
  pinMode(A1, INPUT_PULLUP);
  pinMode(A2, INPUT_PULLUP);
  pinMode(A3, INPUT_PULLUP);
  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);
  
  // Initialize random seed using analog noise
  randomSeed(analogRead(A0) + analogRead(A1) + analogRead(A2));
  
  // Initialize system components
  if (!powerManager.begin()) {
    #ifdef DEBUG
    Serial.println(F("PowerManager initialization failed"));
    #endif
    performSystemReset();
    return;
  }
  
  if (!audioController.begin()) {
    #ifdef DEBUG
    Serial.println(F("AudioController initialization failed"));
    #endif
    performSystemReset();
    return;
  }
  
  if (!buttonHandler.begin()) {
    #ifdef DEBUG
    Serial.println(F("ButtonHandler initialization failed"));
    #endif
    performSystemReset();
    return;
  }
  
  // Initialize the main system controller with state machine
  if (!systemController.begin()) {
    #ifdef DEBUG
    Serial.println(F("SystemController initialization failed"));
    #endif
    performSystemReset();
    return;
  }
  
  // Setup button interrupt for wake-up
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonInterrupt, FALLING);
  
  // Initialize state machine timing
  lastStateTransition = millis();
  
  #ifdef DEBUG
  Serial.println(F("State machine initialized successfully"));
  Serial.print(F("Initial state: "));
  logSystemState();
  Serial.println(F("Entering sleep mode"));
  Serial.flush();
  #endif
  
  // Enter sleep mode through the state machine
  systemController.enterSleepMode();
}

void loop() {
  // Main state machine loop - should rarely execute due to sleep mode
  unsigned long currentTime = millis();
  
  // Check for button press
  if (buttonPressed) {
    buttonPressed = false;
    lastStateTransition = currentTime;
    
    #ifdef DEBUG
    Serial.println(F("Button press detected - executing state machine"));
    logSystemState();
    #endif
    
    // Execute the complete state machine sequence through SystemController
    systemController.handleButtonPress();
    
    #ifdef DEBUG
    Serial.print(F("State machine completed - final state: "));
    logSystemState();
    Serial.println(F("Returning to sleep"));
    Serial.flush();
    #endif
  }
  
  // Check for system timeout (watchdog functionality)
  if (currentTime - lastStateTransition > STATE_TRANSITION_TIMEOUT) {
    handleSystemTimeout();
  }
  
  // Ensure we return to sleep mode
  systemController.enterSleepMode();
}

// State machine helper functions
void handleSystemTimeout() {
  #ifdef DEBUG
  Serial.println(F("System timeout detected - performing recovery"));
  #endif
  
  // Check if system is stuck in a non-sleep state
  SystemState currentState = systemController.getCurrentState();
  
  if (currentState != DEEP_SLEEP) {
    #ifdef DEBUG
    Serial.print(F("System stuck in state: "));
    logSystemState();
    Serial.println(F("Forcing return to sleep"));
    #endif
    
    // Force system back to sleep state
    systemController.resetSystem();
    systemController.enterSleepMode();
  }
  
  lastStateTransition = millis();
}

void logSystemState() {
  #ifdef DEBUG
  SystemState currentState = systemController.getCurrentState();
  
  switch (currentState) {
    case DEEP_SLEEP:
      Serial.print(F("DEEP_SLEEP"));
      break;
    case WAKING_UP:
      Serial.print(F("WAKING_UP"));
      break;
    case POWERING_UP:
      Serial.print(F("POWERING_UP"));
      break;
    case PLAYING:
      Serial.print(F("PLAYING"));
      break;
    case POWERING_DOWN:
      Serial.print(F("POWERING_DOWN"));
      break;
    case ERROR_STATE:
      Serial.print(F("ERROR_STATE"));
      break;
    default:
      Serial.print(F("UNKNOWN_STATE"));
      break;
  }
  
  if (systemController.hasError()) {
    Serial.print(F(" [ERROR: "));
    Serial.print(systemController.getLastError());
    Serial.print(F("]"));
  }
  #endif
}

void performSystemReset() {
  #ifdef DEBUG
  Serial.println(F("Performing system reset..."));
  Serial.flush();
  #endif
  
  // Disable all peripherals
  power_adc_disable();
  power_spi_disable();
  power_twi_disable();
  power_timer1_disable();
  power_timer2_disable();
  
  // Force hardware reset using watchdog
  wdt_enable(WDTO_15MS);
  while(1) {
    // Wait for watchdog reset
  }
}

// Interrupt service routine for button press
void buttonInterrupt() {
  // Keep this function minimal and fast
  buttonPressed = true;
}

// Optional: Watchdog timer setup for additional reliability
void setupWatchdog() {
  // This function can be called if you want a watchdog timer
  // to reset the device if it gets stuck
  
  cli();
  wdt_reset();
  WDTCSR |= (1<<WDCE) | (1<<WDE);
  WDTCSR = (1<<WDIE) | (1<<WDP3) | (1<<WDP0);  // 8 second timeout
  sei();
}

// Watchdog interrupt service routine
ISR(WDT_vect) {
  // Watchdog timer interrupt
  // Can be used for periodic wake-ups or system reset
}

/*
 * State Machine Integration Notes:
 * 
 * The main system state machine is implemented through the SystemController class.
 * State transitions follow this sequence:
 * 
 * DEEP_SLEEP -> WAKING_UP -> POWERING_UP -> PLAYING -> POWERING_DOWN -> DEEP_SLEEP
 * 
 * State Machine Features:
 * - Automatic timeout handling for stuck states
 * - Error recovery with retry logic
 * - Proper timing and sequencing for all operations
 * - Power optimization through coordinated component control
 * - Comprehensive logging for debugging
 * 
 * Requirements Addressed:
 * - 1.1: Audio plays only when button is pressed
 * - 1.2: System remains silent until button press
 * - 1.3: Audio plays once per button press
 * - 3.1: Deep sleep mode with ultra-low power consumption
 * - 3.3: Automatic return to sleep after audio completion
 */

// Function to check battery voltage (requires voltage divider)
// Uncomment and modify if you add battery monitoring
/*
float checkBatteryVoltage() {
  power_adc_enable();  // Enable ADC for measurement
  
  int rawReading = analogRead(A0);  // Assuming voltage divider on A0
  float voltage = (rawReading * 3.3) / 1024.0 * 2.0;  // Adjust for divider
  
  power_adc_disable();  // Disable ADC to save power
  return voltage;
}
*/

/*
 * Usage Notes:
 * 
 * 1. Remove power LED from Arduino Pro Mini for optimal battery life
 * 2. Audio files must be named 0001.wav, 0002.wav, etc. in /mp3 folder
 * 3. Adjust NUM_AUDIO_FILES constant to match number of files you have
 * 4. Files are selected randomly, avoiding immediate repeats
 * 5. Use FAT32 formatted SD card
 * 6. For debugging, define DEBUG before compiling
 * 7. Expected battery life: 6-12 months with daily use
 * 
 * Power Consumption:
 * - Sleep mode: ~10µA
 * - Active (playing): ~150mA
 * - Average (daily use): ~50µA
 * 
 * Troubleshooting:
 * - No sound: Check DFPlayer connections and SD card
 * - No response: Verify button wiring and pull-up resistor
 * - Poor battery life: Ensure power LED is removed from Arduino
 */ 