#ifndef SYSTEM_CONTROLLER_H
#define SYSTEM_CONTROLLER_H

#include <Arduino.h>
#include "PowerManager.h"
#include "AudioController.h"
#include "ButtonHandler.h"

/**
 * SystemController Class
 * 
 * Integrates power management with audio system for coordinated operation.
 * Manages proper startup/shutdown sequences and error handling.
 * 
 * Key Features:
 * - Coordinated DFPlayer power control with audio playback
 * - Proper startup/shutdown sequences with timing
 * - Error handling for power management failures
 * - State machine for system operation
 * 
 * Requirements addressed: 2.1, 2.2, 3.4, 3.6
 */

enum SystemState {
    DEEP_SLEEP,      // Ultra-low power mode (~10µA)
    WAKING_UP,       // Transitioning from sleep (~20mA)
    POWERING_UP,     // Enabling DFPlayer (~25mA)
    PLAYING,         // Audio playback (~150mA)
    POWERING_DOWN,   // Disabling DFPlayer (~25mA)
    ERROR_STATE      // Error recovery mode
};

class SystemController {
public:
    // Constructor
    SystemController(PowerManager& powerMgr, AudioController& audioCtrl, ButtonHandler& buttonHdlr);
    
    // Initialization
    bool begin();
    
    // Main system operation
    void handleButtonPress();
    void enterSleepMode();
    
    // State management
    SystemState getCurrentState() const;
    bool isSystemReady() const;
    
    // Error handling
    bool hasError() const;
    void clearError();
    const char* getLastError() const;
    
    // Power management integration
    bool powerUpAudioSystem();
    bool powerDownAudioSystem();
    bool initializeAudioSystem();
    
    // Timing and sequencing
    bool waitForSystemReady(unsigned long timeoutMs = 3000);
    void executeStartupSequence();
    void executeShutdownSequence();
    
    // Error recovery
    bool recoverFromError();
    void resetSystem();
    
    // Enhanced error handling and recovery
    bool handleCriticalError();
    bool performSystemDiagnostics();
    bool validateAllComponents();
    void enableGracefulDegradation();
    bool isInDegradedMode() const;
    void logSystemHealth();
    
    // Status information
    unsigned long getLastOperationTime() const;
    unsigned long getTotalOperationTime() const;
    
private:
    // Component references
    PowerManager& _powerManager;
    AudioController& _audioController;
    ButtonHandler& _buttonHandler;
    
    // State tracking
    SystemState _currentState;
    SystemState _previousState;
    bool _hasError;
    char _lastError[64];
    
    // Timing information
    unsigned long _stateStartTime;
    unsigned long _lastOperationTime;
    unsigned long _totalOperationTime;
    
    // Configuration constants
    static const unsigned long POWER_UP_TIMEOUT = 2000;
    static const unsigned long AUDIO_INIT_TIMEOUT = 3000;
    static const unsigned long AUDIO_PLAY_TIMEOUT = 5000;
    static const unsigned long POWER_DOWN_TIMEOUT = 1000;
    static const unsigned long ERROR_RECOVERY_DELAY = 500;
    static const int MAX_ERROR_RECOVERY_ATTEMPTS = 3;
    
    // Error recovery tracking
    int _errorRecoveryAttempts;
    unsigned long _lastErrorTime;
    
    // Enhanced error handling
    bool _degradedMode;
    bool _criticalError;
    unsigned long _lastDiagnosticsTime;
    int _totalErrorCount;
    bool _componentValidationPassed;
    
    // Private methods
    void setState(SystemState newState);
    bool validateSystemState();
    void logError(const char* error);
    void logStateTransition(SystemState from, SystemState to);
    
    // Startup sequence steps
    bool stepPowerUpDFPlayer();
    bool stepWaitForDFPlayerReady();
    bool stepInitializeAudioController();
    bool stepValidateAudioSystem();
    
    // Shutdown sequence steps
    bool stepStopAudio();
    bool stepPowerDownDFPlayer();
    bool stepValidatePowerDown();
    
    // Error handling helpers
    bool handlePowerUpError();
    bool handleAudioInitError();
    bool handlePlaybackError();
    bool handlePowerDownError();
};

#endif // SYSTEM_CONTROLLER_H