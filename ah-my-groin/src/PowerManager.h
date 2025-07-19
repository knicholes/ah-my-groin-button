#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

/**
 * PowerManager Class
 * 
 * Manages ultra-low power consumption for the button-triggered audio device.
 * Provides deep sleep functionality with interrupt-driven wake-up capability.
 * 
 * Key Features:
 * - Deep sleep mode with ≤10µA current consumption
 * - Interrupt-driven button wake-up
 * - DFPlayer power control via enable pin
 * - Peripheral power management
 * - Watchdog timer support
 */
class PowerManager {
public:
    // Constructor
    PowerManager(int dfPlayerEnablePin = 5, int buttonPin = 2);
    
    // Initialization
    void begin();
    
    // Sleep management
    void enterDeepSleep();
    void wakeFromSleep();
    bool isAwake() const;
    
    // DFPlayer power control
    void enableDFPlayer();
    void disableDFPlayer();
    bool isDFPlayerEnabled() const;
    void powerUpDFPlayer();
    void powerDownDFPlayer();
    bool waitForDFPlayerReady(unsigned long timeoutMs = 2000);
    
    // Power optimization
    void disableUnusedPeripherals();
    void enableAllPeripherals();
    void optimizeForMinimalPower();
    void disableAllNonEssentialPeripherals();
    void enableMinimalPeripherals();
    
    // Power consumption monitoring
    void startPowerMeasurement();
    void stopPowerMeasurement();
    unsigned long getActiveDuration() const;
    float estimateCurrentConsumption() const;
    bool validatePowerConsumption() const;
    void logPowerConsumption() const;
    
    // Button interrupt management
    void setupButtonInterrupt();
    static void buttonInterruptHandler();
    
    // Watchdog timer (optional)
    void enableWatchdog(uint8_t timeout = WDTO_8S);
    void disableWatchdog();
    void resetWatchdog();
    
    // Power state information
    unsigned long getLastWakeTime() const;
    unsigned long getSleepDuration() const;
    
    // Enhanced error handling and recovery
    bool hasError() const;
    void clearError();
    const char* getLastError() const;
    bool recoverFromError();
    bool validatePowerState();
    int getErrorCount() const;
    void resetErrorCount();
    
private:
    // Pin assignments
    int _dfPlayerEnablePin;
    int _buttonPin;
    
    // State tracking
    bool _isAwake;
    bool _dfPlayerEnabled;
    bool _watchdogEnabled;
    unsigned long _lastWakeTime;
    unsigned long _sleepStartTime;
    
    // Enhanced error tracking
    bool _hasError;
    char _lastError[64];
    int _errorCount;
    unsigned long _lastErrorTime;
    
    // Power consumption monitoring
    unsigned long _powerMeasurementStart;
    unsigned long _totalActiveDuration;
    unsigned long _lastActiveDuration;
    bool _powerMeasurementActive;
    
    // Static instance for interrupt handling
    static PowerManager* _instance;
    
    // Private methods
    void configureSleepMode();
    void disableBrownOutDetector();
    void enableBrownOutDetector();
    void logError(const char* error);
};

// Global instance declaration (defined in PowerManager.cpp)
extern PowerManager powerManager;

#endif // POWER_MANAGER_H