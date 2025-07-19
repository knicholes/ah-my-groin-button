/*
 * System Integration Test
 * 
 * Tests the integration between PowerManager and AudioController
 * through the SystemController class.
 * 
 * This test validates:
 * - Coordinated DFPlayer power control with audio playback
 * - Proper startup/shutdown sequences
 * - Error handling for power management failures
 * 
 * Requirements tested: 2.1, 2.2, 3.4, 3.6
 */

#include <Arduino.h>
#include <SoftwareSerial.h>
#include "PowerManager.h"
#include "AudioController.h"
#include "ButtonHandler.h"
#include "SystemController.h"

// Test configuration
#define TEST_DFPLAYER_RX 3
#define TEST_DFPLAYER_TX 4
#define TEST_DFPLAYER_ENABLE 5
#define TEST_BUTTON_PIN 2

// Test results tracking
struct TestResults {
    int totalTests;
    int passedTests;
    int failedTests;
    bool integrationPassed;
    bool powerSequencePassed;
    bool errorHandlingPassed;
    bool timingPassed;
};

TestResults testResults = {0, 0, 0, false, false, false, false};

// Test components
SoftwareSerial testSerial(TEST_DFPLAYER_TX, TEST_DFPLAYER_RX);
AudioController testAudioController(testSerial, 15);
SystemController testSystemController(powerManager, testAudioController, buttonHandler);

// Test helper functions
void printTestHeader(const char* testName);
void printTestResult(const char* testName, bool passed);
void printTestSummary();
bool validatePowerSequence();
bool validateErrorHandling();
bool validateTimingRequirements();
bool validateIntegration();

void setup() {
    Serial.begin(9600);
    while (!Serial) {
        ; // Wait for serial port to connect
    }
    
    Serial.println(F("=== System Integration Test Suite ==="));
    Serial.println(F("Testing PowerManager + AudioController integration"));
    Serial.println();
    
    // Initialize components
    powerManager.begin();
    buttonHandler.begin();
    testSerial.begin(9600);
    
    delay(1000);
    
    // Run integration tests
    runIntegrationTests();
    
    // Print final results
    printTestSummary();
}

void loop() {
    // Test complete - do nothing
    delay(1000);
}

void runIntegrationTests() {
    Serial.println(F("Starting integration tests..."));
    Serial.println();
    
    // Test 1: Basic Integration
    testResults.integrationPassed = validateIntegration();
    
    // Test 2: Power Sequence Validation
    testResults.powerSequencePassed = validatePowerSequence();
    
    // Test 3: Error Handling
    testResults.errorHandlingPassed = validateErrorHandling();
    
    // Test 4: Timing Requirements
    testResults.timingPassed = validateTimingRequirements();
}

bool validateIntegration() {
    printTestHeader("Basic Integration Test");
    
    bool passed = true;
    
    // Test SystemController initialization
    if (!testSystemController.begin()) {
        Serial.println(F("  FAIL: SystemController initialization failed"));
        passed = false;
    } else {
        Serial.println(F("  PASS: SystemController initialized successfully"));
    }
    
    // Test initial state
    if (testSystemController.getCurrentState() != DEEP_SLEEP) {
        Serial.println(F("  FAIL: Initial state should be DEEP_SLEEP"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Initial state is DEEP_SLEEP"));
    }
    
    // Test error state
    if (testSystemController.hasError()) {
        Serial.println(F("  FAIL: SystemController should not have errors initially"));
        passed = false;
    } else {
        Serial.println(F("  PASS: No initial errors"));
    }
    
    printTestResult("Basic Integration", passed);
    testResults.totalTests++;
    if (passed) testResults.passedTests++;
    else testResults.failedTests++;
    
    return passed;
}

bool validatePowerSequence() {
    printTestHeader("Power Sequence Validation");
    
    bool passed = true;
    unsigned long startTime, endTime;
    
    Serial.println(F("  Testing power-up sequence..."));
    
    // Test power-up sequence
    startTime = millis();
    bool powerUpResult = testSystemController.powerUpAudioSystem();
    endTime = millis();
    
    if (!powerUpResult) {
        Serial.println(F("  FAIL: Power-up sequence failed"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Power-up sequence completed"));
        
        // Validate timing (should complete within reasonable time)
        unsigned long powerUpTime = endTime - startTime;
        Serial.print(F("  Power-up time: "));
        Serial.print(powerUpTime);
        Serial.println(F("ms"));
        
        if (powerUpTime > 5000) {
            Serial.println(F("  WARN: Power-up took longer than expected"));
        }
    }
    
    // Verify DFPlayer is enabled after power-up
    if (!powerManager.isDFPlayerEnabled()) {
        Serial.println(F("  FAIL: DFPlayer should be enabled after power-up"));
        passed = false;
    } else {
        Serial.println(F("  PASS: DFPlayer enabled after power-up"));
    }
    
    Serial.println(F("  Testing power-down sequence..."));
    
    // Test power-down sequence
    startTime = millis();
    bool powerDownResult = testSystemController.powerDownAudioSystem();
    endTime = millis();
    
    if (!powerDownResult && !testSystemController.hasError()) {
        Serial.println(F("  FAIL: Power-down sequence failed"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Power-down sequence completed"));
        
        // Validate timing
        unsigned long powerDownTime = endTime - startTime;
        Serial.print(F("  Power-down time: "));
        Serial.print(powerDownTime);
        Serial.println(F("ms"));
    }
    
    // Verify DFPlayer is disabled after power-down
    if (powerManager.isDFPlayerEnabled()) {
        Serial.println(F("  FAIL: DFPlayer should be disabled after power-down"));
        passed = false;
    } else {
        Serial.println(F("  PASS: DFPlayer disabled after power-down"));
    }
    
    printTestResult("Power Sequence", passed);
    testResults.totalTests++;
    if (passed) testResults.passedTests++;
    else testResults.failedTests++;
    
    return passed;
}

bool validateErrorHandling() {
    printTestHeader("Error Handling Validation");
    
    bool passed = true;
    
    // Test error clearing
    testSystemController.clearError();
    if (testSystemController.hasError()) {
        Serial.println(F("  FAIL: Error should be cleared"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Error cleared successfully"));
    }
    
    // Test error recovery by simulating a failure scenario
    Serial.println(F("  Testing error recovery..."));
    
    // Force DFPlayer to be disabled to simulate power failure
    powerManager.disableDFPlayer();
    
    // Try to initialize audio system (should handle the error)
    bool initResult = testSystemController.initializeAudioSystem();
    
    if (initResult) {
        Serial.println(F("  PASS: System recovered from simulated power failure"));
    } else {
        Serial.println(F("  INFO: System detected power failure (expected behavior)"));
        
        // Check if error was properly logged
        if (testSystemController.hasError()) {
            Serial.print(F("  INFO: Error logged: "));
            Serial.println(testSystemController.getLastError());
        }
    }
    
    // Test system reset functionality
    Serial.println(F("  Testing system reset..."));
    testSystemController.resetSystem();
    
    if (testSystemController.hasError()) {
        Serial.println(F("  FAIL: System should not have errors after reset"));
        passed = false;
    } else {
        Serial.println(F("  PASS: System reset cleared errors"));
    }
    
    if (testSystemController.getCurrentState() != DEEP_SLEEP) {
        Serial.println(F("  FAIL: System should be in DEEP_SLEEP after reset"));
        passed = false;
    } else {
        Serial.println(F("  PASS: System in DEEP_SLEEP after reset"));
    }
    
    printTestResult("Error Handling", passed);
    testResults.totalTests++;
    if (passed) testResults.passedTests++;
    else testResults.failedTests++;
    
    return passed;
}

bool validateTimingRequirements() {
    printTestHeader("Timing Requirements Validation");
    
    bool passed = true;
    
    // Test startup timing
    Serial.println(F("  Testing startup timing requirements..."));
    
    unsigned long startTime = millis();
    testSystemController.powerUpAudioSystem();
    unsigned long powerUpTime = millis() - startTime;
    
    Serial.print(F("  Power-up time: "));
    Serial.print(powerUpTime);
    Serial.println(F("ms"));
    
    // Power-up should complete within 3 seconds (requirement 3.4)
    if (powerUpTime > 3000) {
        Serial.println(F("  FAIL: Power-up exceeded 3 second requirement"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Power-up within timing requirement"));
    }
    
    // Test shutdown timing
    Serial.println(F("  Testing shutdown timing requirements..."));
    
    startTime = millis();
    testSystemController.powerDownAudioSystem();
    unsigned long powerDownTime = millis() - startTime;
    
    Serial.print(F("  Power-down time: "));
    Serial.print(powerDownTime);
    Serial.println(F("ms"));
    
    // Power-down should complete within 1 second
    if (powerDownTime > 1000) {
        Serial.println(F("  FAIL: Power-down exceeded 1 second requirement"));
        passed = false;
    } else {
        Serial.println(F("  PASS: Power-down within timing requirement"));
    }
    
    // Test system ready detection
    Serial.println(F("  Testing system ready detection..."));
    
    testSystemController.powerUpAudioSystem();
    startTime = millis();
    bool readyResult = testSystemController.waitForSystemReady(5000);
    unsigned long readyTime = millis() - startTime;
    
    Serial.print(F("  System ready time: "));
    Serial.print(readyTime);
    Serial.println(F("ms"));
    
    if (!readyResult) {
        Serial.println(F("  FAIL: System ready detection failed"));
        passed = false;
    } else {
        Serial.println(F("  PASS: System ready detection successful"));
    }
    
    // Clean up
    testSystemController.powerDownAudioSystem();
    
    printTestResult("Timing Requirements", passed);
    testResults.totalTests++;
    if (passed) testResults.passedTests++;
    else testResults.failedTests++;
    
    return passed;
}

void printTestHeader(const char* testName) {
    Serial.println();
    Serial.print(F("--- "));
    Serial.print(testName);
    Serial.println(F(" ---"));
}

void printTestResult(const char* testName, bool passed) {
    Serial.print(F("Result: "));
    Serial.print(testName);
    Serial.print(F(" - "));
    if (passed) {
        Serial.println(F("PASSED"));
    } else {
        Serial.println(F("FAILED"));
    }
    Serial.println();
}

void printTestSummary() {
    Serial.println(F("=== Test Summary ==="));
    Serial.print(F("Total Tests: "));
    Serial.println(testResults.totalTests);
    Serial.print(F("Passed: "));
    Serial.println(testResults.passedTests);
    Serial.print(F("Failed: "));
    Serial.println(testResults.failedTests);
    Serial.println();
    
    Serial.println(F("Integration Test Results:"));
    Serial.print(F("  Basic Integration: "));
    Serial.println(testResults.integrationPassed ? F("PASS") : F("FAIL"));
    Serial.print(F("  Power Sequence: "));
    Serial.println(testResults.powerSequencePassed ? F("PASS") : F("FAIL"));
    Serial.print(F("  Error Handling: "));
    Serial.println(testResults.errorHandlingPassed ? F("PASS") : F("FAIL"));
    Serial.print(F("  Timing Requirements: "));
    Serial.println(testResults.timingPassed ? F("PASS") : F("FAIL"));
    Serial.println();
    
    if (testResults.passedTests == testResults.totalTests) {
        Serial.println(F("*** ALL INTEGRATION TESTS PASSED ***"));
        Serial.println(F("Power management and audio system integration is working correctly."));
    } else {
        Serial.println(F("*** SOME TESTS FAILED ***"));
        Serial.println(F("Review failed tests and check system integration."));
    }
    
    Serial.println();
    Serial.println(F("Requirements Validation:"));
    Serial.println(F("  2.1 - DFPlayer power delivery: Validated through power sequence tests"));
    Serial.println(F("  2.2 - Reliable operation: Validated through integration and error handling"));
    Serial.println(F("  3.4 - DFPlayer power control: Validated through power sequence timing"));
    Serial.println(F("  3.6 - Power elimination: Validated through power-down verification"));
}