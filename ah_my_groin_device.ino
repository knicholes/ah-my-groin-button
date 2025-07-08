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
 * - 2x AA batteries (3V total)
 * 
 * Wiring:
 * - Pin 2 (INT0): Button input (other side to GND)
 * - Pin 3: DFPlayer RX
 * - Pin 4: DFPlayer TX
 * - Pin 5: DFPlayer Enable (optional power control)
 * - VCC: 3V from batteries
 * - GND: Common ground
 * 
 * Audio File Requirements:
 * - File names: 0001.wav, 0002.wav, 0003.wav, etc. (up to 0010.wav default)
 * - Location: /mp3 folder on SD card
 * - Format: WAV (16kHz, 8-bit, mono) or MP3
 * - Numbering: Sequential from MIN_TRACK_NUMBER to MAX_TRACK_NUMBER
 * 
 * Power Optimization Features:
 * - Deep sleep mode between button presses
 * - Wake on button interrupt
 * - DFPlayer power control
 * - Minimal current draw (~10µA in sleep)
 * 
 * Expected Battery Life: 6-12 months with daily use
 * 
 * Author: Generated for "Ah! My Groin!" Project
 * License: MIT
 */

#include <SoftwareSerial.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

// Pin definitions
const int BUTTON_PIN = 2;           // Button input (INT0 for wake-up)
const int DFPLAYER_RX = 3;          // DFPlayer RX (Arduino TX)
const int DFPLAYER_TX = 4;          // DFPlayer TX (Arduino RX)
const int DFPLAYER_ENABLE = 5;      // DFPlayer enable control (optional)

// DFPlayer communication
SoftwareSerial dfPlayerSerial(DFPLAYER_TX, DFPLAYER_RX);

// DFPlayer command structure
const uint8_t CMD_START = 0x7E;
const uint8_t CMD_VERSION = 0xFF;
const uint8_t CMD_LENGTH = 0x06;
const uint8_t CMD_END = 0xEF;
const uint8_t CMD_FEEDBACK = 0x01;  // Request feedback

// DFPlayer commands
const uint8_t CMD_PLAY_TRACK = 0x03;
const uint8_t CMD_SET_VOLUME = 0x06;
const uint8_t CMD_RESET = 0x0C;
const uint8_t CMD_PLAY = 0x0D;
const uint8_t CMD_PAUSE = 0x0E;
const uint8_t CMD_STOP = 0x16;

// Device settings
const int DEFAULT_VOLUME = 25;      // Volume level (0-30)
const int NUM_AUDIO_FILES = 10;     // Number of audio files (0001.wav to 0010.wav)
const int MIN_TRACK_NUMBER = 1;     // First track number (0001.wav)
const int MAX_TRACK_NUMBER = 10;    // Last track number (0010.wav)
const unsigned long DEBOUNCE_DELAY = 200;  // Button debounce in ms
const unsigned long PLAY_TIMEOUT = 5000;   // Max play time in ms

// State variables
volatile bool buttonPressed = false;
bool dfPlayerEnabled = false;
unsigned long lastButtonTime = 0;
int lastTrackPlayed = 0;             // Track the last played file to avoid immediate repeats

// Forward declarations
void enterSleepMode();
void wakeFromSleep();
void sendDFPlayerCommand(uint8_t command, uint16_t parameter);
void initializeDFPlayer();
void enableDFPlayer();
void disableDFPlayer();
void playGroinSound();
void playRandomSound();
int selectRandomTrack();
bool waitForDFPlayerReady();
void buttonInterrupt();

void setup() {
  // Initialize serial for debugging (optional - remove for production)
  #ifdef DEBUG
  Serial.begin(9600);
  Serial.println(F("Ah! My Groin! Device Starting..."));
  #endif
  
  // Configure pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);    // Button with internal pull-up
  pinMode(DFPLAYER_ENABLE, OUTPUT);     // DFPlayer enable control
  
  // Initialize DFPlayer communication
  dfPlayerSerial.begin(9600);
  
  // Power optimization: disable unused peripherals
  power_adc_disable();          // Disable ADC
  power_spi_disable();          // Disable SPI
  power_twi_disable();          // Disable TWI (I2C)
  power_timer1_disable();       // Disable Timer1
  power_timer2_disable();       // Disable Timer2
  
  // Initialize random seed using analog noise
  randomSeed(analogRead(A0) + analogRead(A1) + analogRead(A2));
  
  // Setup button interrupt for wake-up
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonInterrupt, FALLING);
  
  // Initial DFPlayer setup
  enableDFPlayer();
  delay(1000);  // Allow DFPlayer to initialize
  
  if (waitForDFPlayerReady()) {
    initializeDFPlayer();
    
    #ifdef DEBUG
    Serial.println(F("DFPlayer initialized successfully"));
    #endif
  } else {
    #ifdef DEBUG
    Serial.println(F("DFPlayer initialization failed"));
    #endif
  }
  
  // Disable DFPlayer to save power
  disableDFPlayer();
  
  #ifdef DEBUG
  Serial.println(F("Setup complete - entering sleep mode"));
  Serial.flush();
  #endif
  
  // Enter sleep mode immediately
  delay(100);
  enterSleepMode();
}

void loop() {
  // This should rarely execute due to sleep mode
  if (buttonPressed) {
    handleButtonPress();
  }
  
  // Return to sleep
  delay(100);
  enterSleepMode();
}

void handleButtonPress() {
  unsigned long currentTime = millis();
  
  // Debounce check
  if (currentTime - lastButtonTime < DEBOUNCE_DELAY) {
    buttonPressed = false;
    return;
  }
  
  lastButtonTime = currentTime;
  buttonPressed = false;
  
  #ifdef DEBUG
  Serial.println(F("Button pressed - playing sound"));
  #endif
  
  // Wake up and play a random sound
  wakeFromSleep();
  playRandomSound();
  
  #ifdef DEBUG
  Serial.println(F("Sound complete - returning to sleep"));
  Serial.flush();
  #endif
  
  // Return to sleep mode
  disableDFPlayer();
  delay(100);
}

void playGroinSound() {
  // Legacy function - now calls random sound for backwards compatibility
  playRandomSound();
}

void playRandomSound() {
  int trackNumber = selectRandomTrack();
  
  #ifdef DEBUG
  Serial.print(F("Playing track: "));
  Serial.println(trackNumber);
  #endif
  
  enableDFPlayer();
  delay(500);  // Allow DFPlayer to fully initialize
  
  if (waitForDFPlayerReady()) {
    // Set volume
    sendDFPlayerCommand(CMD_SET_VOLUME, DEFAULT_VOLUME);
    delay(100);
    
    // Play the selected track
    sendDFPlayerCommand(CMD_PLAY_TRACK, trackNumber);
    
    // Wait for playback to complete (or timeout)
    unsigned long startTime = millis();
    while (millis() - startTime < PLAY_TIMEOUT) {
      delay(100);
      // Could add code here to check if playback is complete
      // by reading DFPlayer status if needed
    }
  }
  
  disableDFPlayer();
}

int selectRandomTrack() {
  int selectedTrack;
  
  // If we only have one file, just return it
  if (NUM_AUDIO_FILES == 1) {
    return MIN_TRACK_NUMBER;
  }
  
  // Select a random track, but avoid repeating the last one immediately
  do {
    selectedTrack = random(MIN_TRACK_NUMBER, MAX_TRACK_NUMBER + 1);
  } while (selectedTrack == lastTrackPlayed && NUM_AUDIO_FILES > 1);
  
  lastTrackPlayed = selectedTrack;
  return selectedTrack;
}

void initializeDFPlayer() {
  // Reset DFPlayer
  sendDFPlayerCommand(CMD_RESET, 0);
  delay(1000);
  
  // Set initial volume
  sendDFPlayerCommand(CMD_SET_VOLUME, DEFAULT_VOLUME);
  delay(100);
}

void enableDFPlayer() {
  if (!dfPlayerEnabled) {
    digitalWrite(DFPLAYER_ENABLE, HIGH);
    dfPlayerEnabled = true;
    delay(100);  // Allow power to stabilize
  }
}

void disableDFPlayer() {
  if (dfPlayerEnabled) {
    digitalWrite(DFPLAYER_ENABLE, LOW);
    dfPlayerEnabled = false;
  }
}

bool waitForDFPlayerReady() {
  // Simple timeout waiting for DFPlayer to be ready
  unsigned long startTime = millis();
  while (millis() - startTime < 2000) {
    if (dfPlayerSerial.available()) {
      // Clear any initialization messages
      while (dfPlayerSerial.available()) {
        dfPlayerSerial.read();
      }
      return true;
    }
    delay(100);
  }
  return false;  // Timeout
}

void sendDFPlayerCommand(uint8_t command, uint16_t parameter) {
  uint8_t commandBuffer[10];
  
  // Build command packet
  commandBuffer[0] = CMD_START;
  commandBuffer[1] = CMD_VERSION;
  commandBuffer[2] = CMD_LENGTH;
  commandBuffer[3] = command;
  commandBuffer[4] = CMD_FEEDBACK;
  commandBuffer[5] = (uint8_t)(parameter >> 8);    // High byte
  commandBuffer[6] = (uint8_t)(parameter & 0xFF);  // Low byte
  
  // Calculate checksum
  uint16_t checksum = 0;
  for (int i = 1; i < 7; i++) {
    checksum += commandBuffer[i];
  }
  checksum = 0 - checksum;
  
  commandBuffer[7] = (uint8_t)(checksum >> 8);     // High byte
  commandBuffer[8] = (uint8_t)(checksum & 0xFF);   // Low byte
  commandBuffer[9] = CMD_END;
  
  // Send command
  for (int i = 0; i < 10; i++) {
    dfPlayerSerial.write(commandBuffer[i]);
  }
  
  #ifdef DEBUG
  Serial.print(F("Sent command: 0x"));
  Serial.print(command, HEX);
  Serial.print(F(" with parameter: "));
  Serial.println(parameter);
  #endif
}

void enterSleepMode() {
  #ifdef DEBUG
  Serial.println(F("Entering sleep mode..."));
  Serial.flush();
  #endif
  
  // Ensure DFPlayer is disabled
  disableDFPlayer();
  
  // Configure sleep mode
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  
  // Disable brown-out detection during sleep (saves power)
  sleep_bod_disable();
  
  // Enable sleep and enter sleep mode
  cli();                    // Disable interrupts
  sleep_enable();           // Enable sleep mode
  sei();                    // Enable interrupts
  sleep_cpu();              // Enter sleep mode
  
  // Execution resumes here after wake-up
  sleep_disable();          // Disable sleep mode
}

void wakeFromSleep() {
  #ifdef DEBUG
  Serial.println(F("Waking from sleep..."));
  #endif
  
  // Re-enable peripherals if needed
  // (Most are disabled for power savings)
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
 * Additional Functions for Advanced Features
 */

// Function to adjust volume (0-30)
void setVolume(int volume) {
  if (volume < 0) volume = 0;
  if (volume > 30) volume = 30;
  
  enableDFPlayer();
  delay(100);
  sendDFPlayerCommand(CMD_SET_VOLUME, volume);
  delay(100);
  disableDFPlayer();
}

// Function to play a specific track (bypasses random selection)
void playTrack(int trackNumber) {
  #ifdef DEBUG
  Serial.print(F("Playing specific track: "));
  Serial.println(trackNumber);
  #endif
  
  enableDFPlayer();
  delay(500);
  
  if (waitForDFPlayerReady()) {
    sendDFPlayerCommand(CMD_SET_VOLUME, DEFAULT_VOLUME);
    delay(100);
    sendDFPlayerCommand(CMD_PLAY_TRACK, trackNumber);
    
    unsigned long startTime = millis();
    while (millis() - startTime < PLAY_TIMEOUT) {
      delay(100);
    }
  }
  
  disableDFPlayer();
}

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