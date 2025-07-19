#ifndef TESTING_FRAMEWORK_H
#define TESTING_FRAMEWORK_H

#include <Arduino.h>
#include "SystemController.h"
#include "PowerManager.h"
#include "AudioController.h"
#include "ButtonHandler.h"

/**
 * TestingFramework Class
 * 
 * Comprehensive testing and validation framework for the button-triggered audio system.
 * Provides serial debugging output, current consumption measurement helpers,
 * and button press simulation for testing.
 * 
 * Key Features:
 * - Serial debugging output for all power states
 * - Current consumption measurement and validation
 * - Button press simulation and testing functions
 * - System health monitoring and reporting
 * - Automated test sequences
 * 
 * Requirements addressed: 3.1, 3.2, 4.1, 4.2
 */

class TestingFramework {
public:
    // Constructor
    TestingFramework(SystemController& sysCtrl, PowerManager& powerMgr, 
                    AudioController& audioCtrl, ButtonHandler& buttonHdlr);
    
    // Initialization
    void begin();
    
    // Serial debugging output for power states
    void enablePowerStateDebugging(bool enable = true);
    void logCurrentPowerState();
    void logPowerStateTransition(SystemState from, SystemState to);
    void logDetailedPowerConsumption();
    void logBatteryLifeEstimate();
    
    // Current consumption measurement helpers
    void startCurrentMeasurement();
    void stopCurrentMeasurement();
    float getCurrentConsumption();
    float getAverageConsumption();
    bool validatePowerRequirements();
    void logPowerProfile();
    void measureSleepCurrent();
    void measureActiveCurrent();
    
    // Button press simulation and testing
    void simulateButtonPress();
    void simulateButtonRelease();
    void simulateButtonBounce();
    void testButtonDebouncing();
    void testButtonInterruptWakeup();
    bool validateButtonResponse();
    
    // Automated test sequences
    void runFullSystemTest();
    void runPowerConsumptionTest();
    void runButtonFunctionalityTest();
    void runAudioSystemTest();
    void runErrorRecoveryTest();
    
    // System health monitoring
    void logSystemHealth();
    void monitorSystemPerformance();
    bool validateSystemRequirements();
    void generateTestReport();
    
    // Test configuration
    void setTestMode(bool enabled);
    void setVerboseLogging(bool enabled);
    void setCurrentMeasurementPin(int pin);
    
    // Test results
    struct TestResults {
        bool powerRequirementsMet;
        bool buttonFunctionalityPassed;
        bool audioSystemPassed;
        bool errorRecoveryPassed;
        float averageCurrentConsumption;
        float sleepCurrentConsumption;
        float activeCurrentConsumption;
        unsigned long averageResponseTime;
        int totalErrors;
        bool overallTestPassed;
    };
    
    TestResults getLastTestResults() const;
    void printTestResults() const;
    
private:
    // Component references
    SystemController& _systemController;
    PowerManager& _powerManager;
    AudioController& _audioController;
    ButtonHandler& _buttonHandler;
    
    // Test configuration
    bool _testModeEnabled;
    bool _verboseLogging;
    bool _powerStateDebugging;
    int _currentMeasurementPin;
    
    // Current measurement tracking
    unsigned long _measurementStartTime;
    float _totalCurrentMeasured;
    int _measurementCount;
    float _lastCurrentReading;
    bool _measurementActive;
    
    // Test results tracking
    TestResults _lastResults;
    unsigned long _testStartTime;
    int _testCount;
    
    // Power state tracking for debugging
    SystemState _lastLoggedState;
    unsigned long _stateStartTime;
    float _stateCurrentConsumption[6]; // One for each SystemState
    unsigned long _stateDuration[6];
    
    // Button simulation
    volatile bool _simulatedButtonState;
    unsigned long _lastSimulationTime;
    
    // Private helper methods
    void initializeTestFramework();
    void resetTestResults();
    float measureAnalogCurrent();
    void logPowerStateDetails(SystemState state);
    void validatePowerState(SystemState state);
    bool testSingleButtonPress();
    bool testButtonDebounceScenario();
    void simulateButtonBouncePattern();
    void logTestStep(const char* stepName, bool passed);
    void calculateBatteryLife();
    
    // Test constants
    static const float SLEEP_CURRENT_REQUIREMENT; // 10µA = 0.01mA
    static const float MAX_ACTIVE_CURRENT; // 200mA maximum
    static const unsigned long BUTTON_RESPONSE_TIMEOUT; // 100ms
    static const int DEBOUNCE_TEST_ITERATIONS; // 10 iterations
    static const unsigned long TEST_TIMEOUT; // 30 seconds
};

#endif // TESTING_FRAMEWORK_H