#include <Arduino.h>
#include "../src/PowerManager.h"
#include "../src/AudioController.h"
#include "../src/ButtonHandler.h"
#include "../src/SystemController.h"

// Compile test for power optimization functionality
// This file tests that all power optimization code compiles correctly

void testPowerManagerCompilation() {
    // Test PowerManager with power optimization methods
    PowerManager pm(5, 2);
    
    // Test basic functionality
    pm.begin();
    pm.enterDeepSleep();
    pm.wakeFromSleep();
    pm.enableDFPlayer();
    pm.disableDFPlayer();
    pm.powerUpDFPlayer();
    pm.powerDownDFPlayer();
    
    // Test power optimization methods
    pm.optimizeForMinimalPower();
    pm.disableAllNonEssentialPeripherals();
    pm.enableMinimalPeripherals();
    pm.disableUnusedPeripherals();
    pm.enableAllPeripherals();
    
    // Test power monitoring methods
    pm.startPowerMeasurement();
    pm.stopPowerMeasurement();
    unsigned long duration = pm.getActiveDuration();
    float current = pm.estimateCurrentConsumption();
    bool valid = pm.validatePowerConsumption();
    pm.logPowerConsumption();
    
    // Test error handling
    bool hasError = pm.hasError();
    pm.clearError();
    const char* error = pm.getLastError();
    bool recovered = pm.recoverFromError();
    bool stateValid = pm.validatePowerState();
    int errorCount = pm.getErrorCount();
    pm.resetErrorCount();
    
    // Test state queries
    bool awake = pm.isAwake();
    bool dfEnabled = pm.isDFPlayerEnabled();
    unsigned long wakeTime = pm.getLastWakeTime();
    unsigned long sleepDuration = pm.getSleepDuration();
    bool ready = pm.waitForDFPlayerReady(1000);
    
    // Test watchdog
    pm.enableWatchdog();
    pm.disableWatchdog();
    pm.resetWatchdog();
    
    // Suppress unused variable warnings
    (void)duration;
    (void)current;
    (void)valid;
    (void)hasError;
    (void)error;
    (void)recovered;
    (void)stateValid;
    (void)errorCount;
    (void)awake;
    (void)dfEnabled;
    (void)wakeTime;
    (void)sleepDuration;
    (void)ready;
}

void testSystemControllerIntegration() {
    // Test SystemController with power optimization integration
    PowerManager pm(5, 2);
    SoftwareSerial ss(3, 4); // Added SoftwareSerial for AudioController
    AudioController ac(ss);
    ButtonHandler bh(2);
    SystemController sc(pm, ac, bh);
    
    // Test initialization
    sc.begin();
    
    // Test main operations
    sc.handleButtonPress();
    sc.enterSleepMode();
    
    // Test state queries
    SystemState state = sc.getCurrentState();
    bool ready = sc.isSystemReady();
    bool hasError = sc.hasError();
    const char* error = sc.getLastError();
    unsigned long opTime = sc.getLastOperationTime();
    unsigned long totalTime = sc.getTotalOperationTime();
    bool degraded = sc.isInDegradedMode();
    
    // Test error handling
    sc.clearError();
    sc.resetSystem();
    bool waited = sc.waitForSystemReady(1000);
    
    // Suppress unused variable warnings
    (void)state;
    (void)ready;
    (void)hasError;
    (void)error;
    (void)opTime;
    (void)totalTime;
    (void)degraded;
    (void)waited;
}

void testPowerOptimizationConstants() {
    // Test that all power optimization constants and macros compile
    
    // Sleep mode constants
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_bod_disable();
    sleep_enable();
    sleep_disable();
    
    // Power management constants
    power_adc_disable();
    power_spi_disable();
    power_twi_disable();
    power_timer1_disable();
    power_timer2_disable();
    power_all_enable();
    
    // Register manipulation
    ACSR |= (1 << ACD);  // Disable analog comparator
    ADCSRA &= ~(1 << ADEN);  // Disable ADC
    
    // Watchdog constants
    wdt_reset();
    wdt_enable(WDTO_8S);
    wdt_disable();
}

void setup() {
    // Initialize serial for compilation test
    Serial.begin(9600);
    Serial.println(F("Power Optimization Compile Test"));
    
    // Test all compilation units
    testPowerManagerCompilation();
    testSystemControllerIntegration();
    testPowerOptimizationConstants();
    
    Serial.println(F("All power optimization code compiled successfully!"));
}

void loop() {
    // Compilation test - no loop needed
    delay(1000);
}