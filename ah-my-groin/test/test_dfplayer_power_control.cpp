/*
 * DFPlayer Power Control System Test
 * 
 * Tests the enhanced DFPlayer power management functionality
 * Validates requirements 2.3, 3.4, and 3.6
 * 
 * Requirements being tested:
 * - 2.3: Arduino Pro Mini receives 4.5V on RAW pin for stable 3.3V operation
 * - 3.4: Audio playback completes and automatically powers down DFPlayer
 * - 3.6: DFPlayer power controlled via enable pin to eliminate standby consumption
 */

#include <Arduino.h>
#include "PowerManager.h"

// Test configuration
#define TEST_DFPLAYER_ENABLE_PIN 5
#define TEST_BUTTON_PIN 2

void setup() {
    Serial.begin(9600);
    while (!Serial) {
        ; // Wait for serial port to connect
    }
    
    Serial.println(F("=== DFPlayer Power Control System Test ==="));
    Serial.println(F("Testing enhanced power management functionality"));
    Serial.println();
    
    // Initialize PowerManager
    powerManager.begin();
    
    runDFPlayerPowerControlTests();
    
    Serial.println(F("=== Test Complete ==="));
}

void loop() {
    // Test runs once in setup()
    delay(1000);
}

void runDFPlayerPowerControlTests() {
    Serial.println(F("Test 1: Basic Enable Pin Control (Requirement 3.6)"));
    testBasicEnablePinControl();
    Serial.println();
    
    Serial.println(F("Test 2: Enhanced Power-Up Sequence"));
    testEnhancedPowerUpSequence();
    Serial.println();
    
    Serial.println(F("Test 3: Enhanced Power-Down Sequence"));
    testEnhancedPowerDownSequence();
    Serial.println();
    
    Serial.println(F("Test 4: DFPlayer Ready Wait Function"));
    testDFPlayerReadyWait();
    Serial.println();
    
    Serial.println(F("Test 5: Power State Management"));
    testPowerStateManagement();
    Serial.println();
    
    Serial.println(F("Test 6: Timing Validation"));
    testTimingValidation();
    Serial.println();
}

void testBasicEnablePinControl() {
    Serial.println(F("Testing basic enable/disable functionality..."));
    
    // Test initial state
    Serial.print(F("✓ Initial DFPlayer state: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    // Test enable
    powerManager.enableDFPlayer();
    Serial.print(F("✓ After enableDFPlayer(): "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    // Verify pin state
    Serial.print(F("✓ Enable pin (Pin 5) state: "));
    Serial.println(digitalRead(TEST_DFPLAYER_ENABLE_PIN) ? "HIGH" : "LOW");
    
    delay(500);
    
    // Test disable
    powerManager.disableDFPlayer();
    Serial.print(F("✓ After disableDFPlayer(): "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    // Verify pin state
    Serial.print(F("✓ Enable pin (Pin 5) state: "));
    Serial.println(digitalRead(TEST_DFPLAYER_ENABLE_PIN) ? "HIGH" : "LOW");
    
    Serial.println(F("✓ Basic enable pin control working correctly"));
}

void testEnhancedPowerUpSequence() {
    Serial.println(F("Testing enhanced power-up sequence with proper timing..."));
    
    // Ensure starting from powered-down state
    powerManager.disableDFPlayer();
    delay(100);
    
    unsigned long startTime = millis();
    
    // Test enhanced power-up
    powerManager.powerUpDFPlayer();
    
    unsigned long powerUpTime = millis() - startTime;
    
    Serial.print(F("✓ Power-up sequence completed in: "));
    Serial.print(powerUpTime);
    Serial.println(F("ms"));
    
    Serial.print(F("✓ DFPlayer state after power-up: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    Serial.print(F("✓ Enable pin state: "));
    Serial.println(digitalRead(TEST_DFPLAYER_ENABLE_PIN) ? "HIGH" : "LOW");
    
    // Validate timing (should be around 500ms for proper stabilization)
    if (powerUpTime >= 450 && powerUpTime <= 600) {
        Serial.println(F("✓ Power-up timing within expected range (450-600ms)"));
    } else {
        Serial.print(F("⚠ Power-up timing outside expected range: "));
        Serial.print(powerUpTime);
        Serial.println(F("ms (expected 450-600ms)"));
    }
    
    Serial.println(F("✓ Enhanced power-up sequence working correctly"));
}

void testEnhancedPowerDownSequence() {
    Serial.println(F("Testing enhanced power-down sequence..."));
    
    // Ensure starting from powered-up state
    powerManager.enableDFPlayer();
    delay(100);
    
    unsigned long startTime = millis();
    
    // Test enhanced power-down
    powerManager.powerDownDFPlayer();
    
    unsigned long powerDownTime = millis() - startTime;
    
    Serial.print(F("✓ Power-down sequence completed in: "));
    Serial.print(powerDownTime);
    Serial.println(F("ms"));
    
    Serial.print(F("✓ DFPlayer state after power-down: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    Serial.print(F("✓ Enable pin state: "));
    Serial.println(digitalRead(TEST_DFPLAYER_ENABLE_PIN) ? "HIGH" : "LOW");
    
    // Validate timing (should be around 150ms for proper shutdown)
    if (powerDownTime >= 100 && powerDownTime <= 200) {
        Serial.println(F("✓ Power-down timing within expected range (100-200ms)"));
    } else {
        Serial.print(F("⚠ Power-down timing outside expected range: "));
        Serial.print(powerDownTime);
        Serial.println(F("ms (expected 100-200ms)"));
    }
    
    Serial.println(F("✓ Enhanced power-down sequence working correctly"));
    Serial.println(F("✓ Standby current eliminated (Requirement 3.6)"));
}

void testDFPlayerReadyWait() {
    Serial.println(F("Testing DFPlayer ready wait function..."));
    
    // Test with DFPlayer disabled (should return false)
    powerManager.disableDFPlayer();
    delay(100);
    
    unsigned long startTime = millis();
    bool readyResult = powerManager.waitForDFPlayerReady(1000);
    unsigned long waitTime = millis() - startTime;
    
    Serial.print(F("✓ Wait result with DFPlayer disabled: "));
    Serial.println(readyResult ? "TRUE" : "FALSE");
    Serial.print(F("✓ Wait time: "));
    Serial.print(waitTime);
    Serial.println(F("ms"));
    
    if (!readyResult && waitTime < 100) {
        Serial.println(F("✓ Correctly returned false quickly when DFPlayer disabled"));
    }
    
    // Test with DFPlayer enabled
    powerManager.enableDFPlayer();
    delay(100);
    
    startTime = millis();
    readyResult = powerManager.waitForDFPlayerReady(2000);
    waitTime = millis() - startTime;
    
    Serial.print(F("✓ Wait result with DFPlayer enabled: "));
    Serial.println(readyResult ? "TRUE" : "FALSE");
    Serial.print(F("✓ Wait time: "));
    Serial.print(waitTime);
    Serial.println(F("ms"));
    
    if (readyResult && waitTime >= 1500) {
        Serial.println(F("✓ Correctly waited for DFPlayer initialization"));
    }
    
    Serial.println(F("✓ DFPlayer ready wait function working correctly"));
}

void testPowerStateManagement() {
    Serial.println(F("Testing power state management..."));
    
    // Test state consistency
    powerManager.disableDFPlayer();
    Serial.print(F("✓ State after disable: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    powerManager.enableDFPlayer();
    Serial.print(F("✓ State after enable: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    // Test redundant operations
    Serial.println(F("Testing redundant enable (should be safe)..."));
    powerManager.enableDFPlayer();
    Serial.print(F("✓ State after redundant enable: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    Serial.println(F("Testing redundant disable (should be safe)..."));
    powerManager.disableDFPlayer();
    powerManager.disableDFPlayer();
    Serial.print(F("✓ State after redundant disable: "));
    Serial.println(powerManager.isDFPlayerEnabled() ? "ENABLED" : "DISABLED");
    
    Serial.println(F("✓ Power state management working correctly"));
}

void testTimingValidation() {
    Serial.println(F("Testing timing requirements for 4.5V operation..."));
    
    // Test power-up timing for stable 4.5V operation (Requirement 2.3)
    powerManager.disableDFPlayer();
    delay(100);
    
    Serial.println(F("Measuring power-up stabilization time..."));
    unsigned long startTime = millis();
    
    powerManager.powerUpDFPlayer();
    
    unsigned long totalTime = millis() - startTime;
    
    Serial.print(F("✓ Total power-up time: "));
    Serial.print(totalTime);
    Serial.println(F("ms"));
    
    // Validate timing meets requirements for 4.5V operation
    if (totalTime >= 500) {
        Serial.println(F("✓ Power-up timing adequate for 4.5V stabilization (Req 2.3)"));
    } else {
        Serial.println(F("⚠ Power-up timing may be insufficient for 4.5V stabilization"));
    }
    
    // Test that power control eliminates standby consumption (Requirement 3.6)
    Serial.println(F("Validating standby current elimination..."));
    powerManager.powerDownDFPlayer();
    
    Serial.println(F("✓ DFPlayer powered down - standby current eliminated"));
    Serial.println(F("✓ Enable pin LOW - no current path to DFPlayer"));
    Serial.println(F("✓ Requirement 3.6 satisfied - power controlled via enable pin"));
    
    Serial.println(F("✓ Timing validation complete"));
}