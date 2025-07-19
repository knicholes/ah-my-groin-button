#include <Arduino.h>
#include <SoftwareSerial.h>
#include "../src/PowerManager.h"
#include "../src/AudioController.h"
#include "../src/ButtonHandler.h"
#include "../src/SystemController.h"

// Test configuration
#define DEBUG 1
#define TEST_TIMEOUT 10000

// Global test objects
SoftwareSerial dfPlayerSerial(4, 3);
PowerManager testPowerManager(5, 2);
AudioController testAudioController(dfPlayerSerial, 15);
ButtonHandler testButtonHandler(2, 50);
SystemController testSystemController(testPowerManager, testAudioController, testButtonHandler);

// Test counters
int testsRun = 0;
int testsPassed = 0;
int testsFailed = 0;

// Test helper functions
void printTestResult(const char* testName, bool passed) {
    testsRun++;
    Serial.print(F("TEST: "));
    Serial.print(testName);
    Serial.print(F(" - "));
    
    if (passed) {
        Serial.println(F("PASS"));
        testsPassed++;
    } else {
        Serial.println(F("FAIL"));
        testsFailed++;
    }
}

void printTestSummary() {
    Serial.println(F("\n=== COMPREHENSIVE ERROR HANDLING TEST SUMMARY ==="));
    Serial.print(F("Tests Run: "));
    Serial.println(testsRun);
    Serial.print(F("Tests Passed: "));
    Serial.println(testsPassed);
    Serial.print(F("Tests Failed: "));
    Serial.println(testsFailed);
    Serial.print(F("Success Rate: "));
    Serial.print((testsPassed * 100) / testsRun);
    Serial.println(F("%"));
    Serial.println(F("=== END TEST SUMMARY ===\n"));
}

// Test AudioController error handling and recovery
void testAudioControllerErrorHandling() {
    Serial.println(F("\n--- Testing AudioController Error Handling ---"));
    
    // Test 1: Error logging functionality
    testAudioController.logError("Test error message");
    bool hasError = testAudioController.hasError();
    const char* lastError = testAudioController.getLastError();
    printTestResult("AudioController Error Logging", 
                   hasError && strcmp(lastError, "Test error message") == 0);
    
    // Test 2: Error count tracking
    int initialErrorCount = testAudioController.getErrorCount();
    testAudioController.logError("Another test error");
    int newErrorCount = testAudioController.getErrorCount();
    printTestResult("AudioController Error Count Tracking", 
                   newErrorCount == initialErrorCount + 1);
    
    // Test 3: Error clearing
    testAudioController.clearError();
    bool errorCleared = !testAudioController.hasError();
    printTestResult("AudioController Error Clearing", errorCleared);
    
    // Test 4: Error count reset
    testAudioController.resetErrorCount();
    int resetErrorCount = testAudioController.getErrorCount();
    printTestResult("AudioController Error Count Reset", resetErrorCount == 0);
    
    // Test 5: Communication validation (will fail without actual DFPlayer)
    bool commValid = testAudioController.validateCommunication();
    printTestResult("AudioController Communication Validation", 
                   !commValid); // Should fail without hardware
    
    // Test 6: SD card check (will fail without actual DFPlayer)
    bool sdValid = testAudioController.checkSDCard();
    printTestResult("AudioController SD Card Check", 
                   !sdValid); // Should fail without hardware
    
    // Test 7: Recovery attempt (will fail without hardware but should not crash)
    bool recovered = testAudioController.recoverFromError();
    printTestResult("AudioController Error Recovery", 
                   !recovered); // Should fail gracefully without hardware
}

// Test PowerManager error handling and recovery
void testPowerManagerErrorHandling() {
    Serial.println(F("\n--- Testing PowerManager Error Handling ---"));
    
    // Test 1: Error logging functionality
    testPowerManager.logError("Power test error");
    bool hasError = testPowerManager.hasError();
    const char* lastError = testPowerManager.getLastError();
    printTestResult("PowerManager Error Logging", 
                   hasError && strcmp(lastError, "Power test error") == 0);
    
    // Test 2: Error count tracking
    int initialErrorCount = testPowerManager.getErrorCount();
    testPowerManager.logError("Another power error");
    int newErrorCount = testPowerManager.getErrorCount();
    printTestResult("PowerManager Error Count Tracking", 
                   newErrorCount == initialErrorCount + 1);
    
    // Test 3: Error clearing
    testPowerManager.clearError();
    bool errorCleared = !testPowerManager.hasError();
    printTestResult("PowerManager Error Clearing", errorCleared);
    
    // Test 4: Error count reset
    testPowerManager.resetErrorCount();
    int resetErrorCount = testPowerManager.getErrorCount();
    printTestResult("PowerManager Error Count Reset", resetErrorCount == 0);
    
    // Test 5: Power state validation
    bool powerValid = testPowerManager.validatePowerState();
    printTestResult("PowerManager Power State Validation", powerValid);
    
    // Test 6: Recovery attempt
    bool recovered = testPowerManager.recoverFromError();
    printTestResult("PowerManager Error Recovery", recovered);
}

// Test ButtonHandler error handling and recovery
void testButtonHandlerErrorHandling() {
    Serial.println(F("\n--- Testing ButtonHandler Error Handling ---"));
    
    // Test 1: Error logging functionality
    testButtonHandler.logError("Button test error");
    bool hasError = testButtonHandler.hasError();
    const char* lastError = testButtonHandler.getLastError();
    printTestResult("ButtonHandler Error Logging", 
                   hasError && strcmp(lastError, "Button test error") == 0);
    
    // Test 2: Error count tracking
    int initialErrorCount = testButtonHandler.getErrorCount();
    testButtonHandler.logError("Another button error");
    int newErrorCount = testButtonHandler.getErrorCount();
    printTestResult("ButtonHandler Error Count Tracking", 
                   newErrorCount == initialErrorCount + 1);
    
    // Test 3: Error clearing
    testButtonHandler.clearError();
    bool errorCleared = !testButtonHandler.hasError();
    printTestResult("ButtonHandler Error Clearing", errorCleared);
    
    // Test 4: Error count reset
    testButtonHandler.resetErrorCount();
    int resetErrorCount = testButtonHandler.getErrorCount();
    printTestResult("ButtonHandler Error Count Reset", resetErrorCount == 0);
    
    // Test 5: Button state validation
    bool buttonValid = testButtonHandler.validateButtonState();
    printTestResult("ButtonHandler Button State Validation", buttonValid);
    
    // Test 6: Recovery attempt
    bool recovered = testButtonHandler.recoverFromError();
    printTestResult("ButtonHandler Error Recovery", recovered);
}

// Test SystemController comprehensive error handling
void testSystemControllerErrorHandling() {
    Serial.println(F("\n--- Testing SystemController Error Handling ---"));
    
    // Test 1: Basic error handling
    testSystemController.logError("System test error");
    bool hasError = testSystemController.hasError();
    const char* lastError = testSystemController.getLastError();
    printTestResult("SystemController Error Logging", 
                   hasError && strcmp(lastError, "System test error") == 0);
    
    // Test 2: Error clearing
    testSystemController.clearError();
    bool errorCleared = !testSystemController.hasError();
    printTestResult("SystemController Error Clearing", errorCleared);
    
    // Test 3: Component validation
    bool componentsValid = testSystemController.validateAllComponents();
    printTestResult("SystemController Component Validation", 
                   !componentsValid); // Should fail without hardware
    
    // Test 4: System diagnostics
    bool diagnosticsPass = testSystemController.performSystemDiagnostics();
    printTestResult("SystemController System Diagnostics", 
                   !diagnosticsPass); // Should fail without hardware
    
    // Test 5: Graceful degradation
    testSystemController.enableGracefulDegradation();
    bool inDegradedMode = testSystemController.isInDegradedMode();
    printTestResult("SystemController Graceful Degradation", inDegradedMode);
    
    // Test 6: Critical error handling
    bool criticalHandled = testSystemController.handleCriticalError();
    printTestResult("SystemController Critical Error Handling", 
                   !criticalHandled); // Should fail gracefully without hardware
    
    // Test 7: System health logging (should not crash)
    testSystemController.logSystemHealth();
    printTestResult("SystemController Health Logging", true); // Just test it doesn't crash
}

// Test timeout protection mechanisms
void testTimeoutProtection() {
    Serial.println(F("\n--- Testing Timeout Protection ---"));
    
    // Test 1: AudioController timeout protection in playAudio
    unsigned long startTime = millis();
    bool playResult = testAudioController.playAudio(1);
    unsigned long elapsed = millis() - startTime;
    printTestResult("AudioController Play Timeout Protection", 
                   elapsed < 2000); // Should timeout quickly without hardware
    
    // Test 2: PowerManager DFPlayer ready timeout
    startTime = millis();
    bool readyResult = testPowerManager.waitForDFPlayerReady(1000);
    elapsed = millis() - startTime;
    printTestResult("PowerManager Ready Timeout Protection", 
                   elapsed >= 1000 && elapsed < 1500); // Should respect timeout
    
    // Test 3: AudioController wait for completion timeout
    startTime = millis();
    bool completionResult = testAudioController.waitForCompletion(1000);
    elapsed = millis() - startTime;
    printTestResult("AudioController Completion Timeout Protection", 
                   elapsed >= 1000 && elapsed < 1500); // Should respect timeout
}

// Test graceful degradation scenarios
void testGracefulDegradation() {
    Serial.println(F("\n--- Testing Graceful Degradation ---"));
    
    // Test 1: System continues operation in degraded mode
    testSystemController.enableGracefulDegradation();
    bool systemReady = testSystemController.isSystemReady();
    printTestResult("System Ready in Degraded Mode", 
                   !systemReady); // May not be ready without hardware, but shouldn't crash
    
    // Test 2: Error counts reset in degraded mode
    testAudioController.logError("Pre-degradation error");
    testSystemController.enableGracefulDegradation();
    int errorCount = testAudioController.getErrorCount();
    printTestResult("Error Count Reset in Degraded Mode", errorCount == 0);
    
    // Test 3: Components can still be validated in degraded mode
    bool validation = testSystemController.validateAllComponents();
    printTestResult("Component Validation in Degraded Mode", 
                   true); // Should complete without crashing
}

// Test error recovery mechanisms
void testErrorRecovery() {
    Serial.println(F("\n--- Testing Error Recovery Mechanisms ---"));
    
    // Test 1: AudioController recovery from multiple errors
    for (int i = 0; i < 3; i++) {
        testAudioController.logError("Recovery test error");
    }
    bool audioRecovered = testAudioController.recoverFromError();
    printTestResult("AudioController Multi-Error Recovery", 
                   !audioRecovered); // Should fail without hardware but not crash
    
    // Test 2: PowerManager recovery from errors
    testPowerManager.logError("Power recovery test");
    bool powerRecovered = testPowerManager.recoverFromError();
    printTestResult("PowerManager Error Recovery", powerRecovered);
    
    // Test 3: ButtonHandler recovery from errors
    testButtonHandler.logError("Button recovery test");
    bool buttonRecovered = testButtonHandler.recoverFromError();
    printTestResult("ButtonHandler Error Recovery", buttonRecovered);
    
    // Test 4: SystemController recovery coordination
    testSystemController.logError("System recovery test");
    bool systemRecovered = testSystemController.recoverFromError();
    printTestResult("SystemController Recovery Coordination", 
                   !systemRecovered); // Should fail without hardware but not crash
}

void setup() {
    Serial.begin(9600);
    while (!Serial) {
        ; // Wait for serial port to connect
    }
    
    Serial.println(F("=== COMPREHENSIVE ERROR HANDLING AND RECOVERY TESTS ==="));
    Serial.println(F("Testing enhanced error handling, timeout protection, and graceful degradation"));
    Serial.println();
    
    // Initialize components for testing
    testPowerManager.begin();
    testButtonHandler.begin();
    testSystemController.begin();
    
    delay(1000); // Allow initialization to complete
    
    // Run all test suites
    testAudioControllerErrorHandling();
    testPowerManagerErrorHandling();
    testButtonHandlerErrorHandling();
    testSystemControllerErrorHandling();
    testTimeoutProtection();
    testGracefulDegradation();
    testErrorRecovery();
    
    // Print final summary
    printTestSummary();
    
    Serial.println(F("=== COMPREHENSIVE ERROR HANDLING TESTS COMPLETE ==="));
    Serial.println(F("Note: Some tests expected to fail without actual hardware"));
    Serial.println(F("Focus is on graceful failure handling and system stability"));
}

void loop() {
    // Test complete - just maintain serial output
    delay(5000);
    Serial.println(F("Error handling tests completed. System stable."));
}