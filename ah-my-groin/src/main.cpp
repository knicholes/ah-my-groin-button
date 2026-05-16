/*
 * Simple Button-Triggered Audio Device
 * 
 * Plays 0001.wav from SD card when button is pressed.
 * Optimized for ultra-low power consumption using deep sleep.
 * 
 * Hardware:
 * - Arduino Pro Mini 3.3V/8MHz
 * - DFPlayer Mini MP3 module
 * - Button on pin 2 (interrupt capable)
 * - DFPlayer Enable on pin 5 (power control)
 * - DFPlayer RX on pin 3, TX on pin 4
 */

#include <Arduino.h>
#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>
#include <avr/sleep.h>
#include <avr/power.h>

// Pin definitions
#define BUTTON_PIN 2
#define DFPLAYER_RX 3
#define DFPLAYER_TX 4
#define DFPLAYER_ENABLE 5

// Audio settings
#define MAX_VOLUME 30
#define TRACK_NUMBER 1  // Plays 0001.wav

// Global variables (keep minimal for RAM)
SoftwareSerial dfSerial(DFPLAYER_TX, DFPLAYER_RX);
DFRobotDFPlayerMini dfPlayer;
volatile bool buttonPressed = false;
volatile unsigned long lastButtonTime = 0; // Add debounce timing
bool dfPlayerReady = false;

// Forward declarations
void playAudio();
void enterDeepSleep();

// Button interrupt handler with debouncing
void buttonISR() {
    unsigned long currentTime = millis();
    // Debounce: ignore interrupts within 200ms of last press
    if (currentTime - lastButtonTime > 200) {
        // Double-check button is actually pressed (LOW)
        if (digitalRead(BUTTON_PIN) == LOW) {
            buttonPressed = true;
            lastButtonTime = currentTime;
        }
    }
}

void setup() {
  #ifdef DEBUG
  Serial.begin(9600);
    delay(1000);
    Serial.println(F("Simple Audio Device Starting..."));
  #endif
  
    // Configure pins
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(DFPLAYER_ENABLE, OUTPUT);
    digitalWrite(DFPLAYER_ENABLE, LOW); // Start with DFPlayer off
    
    // Setup button interrupt for wake-up
    attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);
    
    // Power optimization - disable unused peripherals
    power_adc_disable();    // Save ~320µA
    power_spi_disable();    // Save ~100µA  
    power_twi_disable();    // Save ~100µA
    power_timer1_disable(); // Save ~50µA
    power_timer2_disable(); // Save ~50µA
    
    // Set unused pins as inputs with pullups to prevent floating
    for (int pin = 6; pin <= 13; pin++) {
        pinMode(pin, INPUT_PULLUP);
    }
    for (int pin = A0; pin <= A5; pin++) {
        pinMode(pin, INPUT_PULLUP);
    }
    
    // Disable analog comparator to save ~40µA
    ACSR |= (1 << ACD);
    
    #ifdef DEBUG
    Serial.println(F("Entering deep sleep - press button to play audio"));
    Serial.flush();
    #endif
    
    // Enter deep sleep immediately
    enterDeepSleep();
}

void loop() {
    // Check if button was pressed (wake-up from sleep)
    if (buttonPressed) {
        buttonPressed = false;
        
        // Additional verification: make sure button is still pressed
        // Wait a moment for any bouncing to settle
        delay(50);
        if (digitalRead(BUTTON_PIN) == LOW) {
            #ifdef DEBUG
            Serial.println(F("Button press confirmed! Playing audio..."));
            #endif
            
            // Play audio
            playAudio();
        } else {
            #ifdef DEBUG
            Serial.println(F("False button trigger detected - ignoring"));
            #endif
        }
  
        #ifdef DEBUG
        Serial.println(F("Returning to sleep..."));
        Serial.flush();
        #endif
  
        // Return to deep sleep
        delay(100); // Brief delay to ensure DFPlayer is fully powered down
        enterDeepSleep();
    }
}

void playAudio() {
    #ifdef DEBUG
    Serial.println(F("Powering up DFPlayer..."));
    #endif
    
    // Power up DFPlayer
    digitalWrite(DFPLAYER_ENABLE, HIGH);
    delay(1200); // Increased from 800ms - give DFPlayer more time to fully boot
    
    #ifdef DEBUG
    Serial.println(F("Initializing DFPlayer communication..."));
    #endif
    
    // Initialize DFPlayer communication
    dfSerial.begin(9600);
    delay(50); // Reduced delay
    
    // Try multiple initialization attempts with shorter delays
    bool initSuccess = false;
    for (int attempt = 1; attempt <= 3; attempt++) {
        #ifdef DEBUG
        Serial.print(F("DFPlayer init attempt "));
        Serial.println(attempt);
        #endif
        
        if (dfPlayer.begin(dfSerial)) {
            initSuccess = true;
            break;
        }
        delay(300); // Reduced from 500ms
    }
    
    if (initSuccess) {
        #ifdef DEBUG
        Serial.println(F("DFPlayer initialized successfully!"));
        #endif
        
        // Set maximum volume for loudest playback
        dfPlayer.volume(MAX_VOLUME);
        delay(100); // Reduced from 200ms
        
        // Try to query file count to ensure SD card is properly read
        #ifdef DEBUG
        Serial.println(F("Checking SD card and files..."));
        #endif
        
        // Give DFPlayer extra time to read SD card properly
        delay(500); // Increased from 300ms
        
        // Try to get file count - this helps ensure SD card is properly initialized
        int fileCount = dfPlayer.readFileCounts();
        delay(300); // Increased from 200ms
        
        #ifdef DEBUG
        Serial.print(F("Volume set to "));
        Serial.println(MAX_VOLUME);
        Serial.print(F("Files detected: "));
        Serial.println(fileCount);
        #endif
        
        // Try playing audio with multiple attempts to guarantee success
        bool playbackSuccess = false;
        for (int playAttempt = 1; playAttempt <= 3; playAttempt++) {
            // Try one play method at a time for better reliability
            #ifdef DEBUG
            Serial.print(F("Play attempt "));
            Serial.print(playAttempt);
            Serial.print(F(" - Playing track "));
            Serial.println(TRACK_NUMBER);
            #endif
            
            // Clear any previous messages
            while (dfPlayer.available()) {
                dfPlayer.readType();
                dfPlayer.read();
            }
            
            // Use only one play method per attempt to avoid confusion
            if (playAttempt == 1) {
                dfPlayer.play(TRACK_NUMBER); // Standard method
                #ifdef DEBUG
                Serial.println(F("Using standard play() method"));
                #endif
            } else if (playAttempt == 2) {
                dfPlayer.playMp3Folder(TRACK_NUMBER); // MP3 folder method
                #ifdef DEBUG
                Serial.println(F("Using playMp3Folder() method"));
                #endif
            } else {
                dfPlayer.playFolder(1, TRACK_NUMBER); // Folder method
                #ifdef DEBUG
                Serial.println(F("Using playFolder() method"));
                #endif
            }
            
            delay(800); // Increased from 500ms - ensure command is fully processed
            
            #ifdef DEBUG
            Serial.println(F("Play commands sent - waiting for response..."));
            #endif
            
            // Wait for playback to start and complete
            unsigned long startTime = millis();
            bool playbackComplete = false;
            bool audioStarted = false;
            bool errorOccurred = false;
            
            #ifdef DEBUG
            Serial.println(F("Waiting for playback response..."));
            #endif
            
            while (millis() - startTime < 30000) { // Increased to 30 seconds for maximum reliability
                if (dfPlayer.available()) {
                    uint8_t type = dfPlayer.readType();
                    int value = dfPlayer.read();
                    
  #ifdef DEBUG
                    Serial.print(F("DFPlayer message - Type: "));
                    Serial.print(type);
                    Serial.print(F(", Value: "));
                    Serial.println(value);
  #endif
  
                    // Type 5 = playback finished successfully
                    if (type == DFPlayerPlayFinished) {
                        playbackComplete = true;
                        playbackSuccess = true;
                        break;
                    }
                    // Type 4 = error - try to reset and recover
                    else if (type == DFPlayerError) {
                        if (value == 2) {
                            #ifdef DEBUG
                            Serial.println(F("ERROR: File not found - stopping and will retry"));
                            #endif
                        } else {
                            #ifdef DEBUG
                            Serial.print(F("ERROR: DFPlayer error code "));
                            Serial.print(value);
                            Serial.println(F(" - stopping and will retry"));
                            #endif
                        }
                        
                        // Stop current playback and mark as error for retry
                        dfPlayer.stop();
                        delay(100);
                        errorOccurred = true;
                        break; // Exit this attempt and try again
                    }
                    // Type 0 or other messages indicate DFPlayer is responding
                    else {
                        audioStarted = true;
                    }
                }
                
                // If we've been waiting a while and got some response, check if it's playing
                if (audioStarted && (millis() - startTime > 25000)) {
                    #ifdef DEBUG
                    Serial.println(F("Assuming playback completed after 25 seconds"));
                    #endif
                    playbackComplete = true;
                    playbackSuccess = true;
                    break;
                }
                
                delay(50); // Reduced from 100ms for more responsive checking
            }
            
            if (playbackSuccess) {
                #ifdef DEBUG
                Serial.println(F("Playback completed successfully!"));
                Serial.print(F("Total playback time: "));
                Serial.print(millis() - startTime);
                Serial.println(F("ms"));
                #endif
                break; // Success - exit retry loop
            } else if (errorOccurred) {
                #ifdef DEBUG
                Serial.print(F("Playback attempt "));
                Serial.print(playAttempt);
                Serial.println(F(" failed with error - retrying..."));
                #endif
                // Add delay before retry to let DFPlayer reset
                delay(500);
            } else {
                #ifdef DEBUG
                Serial.print(F("Playback attempt "));
                Serial.print(playAttempt);
                Serial.println(F(" timed out - retrying..."));
                #endif
                delay(300);
            }
        }
        
        if (!playbackSuccess) {
            #ifdef DEBUG
            Serial.println(F("All playback attempts failed!"));
            Serial.println(F("Check:"));
            Serial.println(F("  - SD card properly inserted"));
            Serial.println(F("  - Audio file named 0001.wav or 0001.mp3"));
            Serial.println(F("  - File in root directory of SD card"));
            Serial.println(F("  - SD card formatted as FAT32"));
            #endif
        }
        
    } else {
        #ifdef DEBUG
        Serial.println(F("DFPlayer initialization failed!"));
        Serial.println(F("Check connections:"));
        Serial.println(F("  Arduino Pin 3 -> DFPlayer RX"));
        Serial.println(F("  Arduino Pin 4 -> DFPlayer TX"));
        Serial.println(F("  Arduino Pin 5 -> DFPlayer Enable (if available)"));
        Serial.println(F("  VCC -> Arduino 3.3V or 5V"));
        Serial.println(F("  GND -> Arduino GND"));
        #endif
    }
    
    #ifdef DEBUG
    Serial.println(F("Powering down DFPlayer..."));
    #endif
    
    // Power down DFPlayer to save battery
    digitalWrite(DFPLAYER_ENABLE, LOW);
    delay(50); // Reduced delay for faster return to sleep
}

void enterDeepSleep() {
    // Ensure DFPlayer is powered down
    digitalWrite(DFPLAYER_ENABLE, LOW);
    
    // Configure sleep mode for minimum power consumption
    set_sleep_mode(SLEEP_MODE_PWR_DOWN); // Deepest sleep (~10µA)
    
    // Disable brown-out detection during sleep (saves ~25µA)
    sleep_bod_disable();
    
    // Enter sleep
    cli();          // Disable interrupts
    sleep_enable(); // Enable sleep mode
    sei();          // Enable interrupts (allows wake-up)
    sleep_cpu();    // Sleep until interrupt
    
    // === WAKE UP POINT ===
    // Execution resumes here after button press
    
    sleep_disable(); // Disable sleep mode
  
  #ifdef DEBUG
    Serial.println(F("Woke from sleep"));
  #endif
}
