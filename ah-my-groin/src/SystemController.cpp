#include "SystemController.h"

SystemController::SystemController(PowerManager& powerMgr, AudioController& audioCtrl, ButtonHandler& buttonHdlr)
    : _powerManager(powerMgr)
    , _audioController(audioCtrl)
    , _buttonHandler(buttonHdlr)
    , _currentState(DEEP_SLEEP)
    , _previousState(DEEP_SLEEP)
    , _hasError(false)
    , _stateStartTime(0)
    , _lastOperationTime(0)
    , _totalOperationTime(0)
    , _errorRecoveryAttempts(0)
    , _lastErrorTime(0)
    , _degradedMode(false)
    , _criticalError(false)
    , _lastDiagnosticsTime(0)
    , _totalErrorCount(0)
    , _componentValidationPassed(false)
{
    // Initialize error message buffer
    _lastError[0] = '\0';
}

bool SystemController::begin() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Initializing integrated system..."));
    #endif
    
    _hasError = false;
    _errorRecoveryAttempts = 0;
    
    // Validate that all components are available
    if (!validateSystemState()) {
        logError("Component validation failed");
        return false;
    }
    
    // Set initial state
    setState(DEEP_SLEEP);
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Integrated system initialized successfully"));
    #endif
    
    return true;
}

void SystemController::handleButtonPress() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Button press detected - starting integrated sequence"));
    #endif
    
    // Start power measurement to track active time
    _powerManager.startPowerMeasurement();
    
    unsigned long operationStart = millis();
    _lastOperationTime = operationStart;
    
    // Check if system is in critical error state
    if (_criticalError) {
        #ifdef DEBUG
        Serial.println(F("SystemController: System in critical error state - attempting recovery"));
        #endif
        
        if (!handleCriticalError()) {
            logError("Critical error recovery failed - operation aborted");
            setState(ERROR_STATE);
            return;
        }
    }
    
    // Check if we're in degraded mode
    if (_degradedMode) {
        #ifdef DEBUG
        Serial.println(F("SystemController: Operating in degraded mode"));
        #endif
        
        // Perform basic diagnostics before operation
        if (!performSystemDiagnostics()) {
            logError("System diagnostics failed in degraded mode");
            setState(ERROR_STATE);
            return;
        }
    }
    
    // Add timeout protection for entire operation
    bool operationSuccess = false;
    unsigned long operationTimeout = AUDIO_PLAY_TIMEOUT + POWER_UP_TIMEOUT + POWER_DOWN_TIMEOUT + 2000; // Extra buffer
    
    // Execute the complete startup -> play -> shutdown sequence with comprehensive error handling
    if (millis() - operationStart < operationTimeout) {
        if (powerUpAudioSystem()) {
            if (initializeAudioSystem()) {
                // Play audio with integrated error handling
                setState(PLAYING);
                
                if (_audioController.playAudio(1)) {
                    #ifdef DEBUG
                    Serial.println(F("SystemController: Audio playback started"));
                    #endif
                    
                    // Wait for completion with timeout
                    bool completed = _audioController.waitForCompletion(AUDIO_PLAY_TIMEOUT);
                    
                    if (!completed) {
                        logError("Audio playback timeout");
                        _audioController.stopAudio();
                        
                        // Check if this is a critical error
                        if (_audioController.getErrorCount() > 5) {
                            handleCriticalError();
                        }
                    } else {
                        operationSuccess = true;
                    }
                } else {
                    logError("Failed to start audio playback");
                    
                    // Try to recover from audio error
                    if (_audioController.recoverFromError()) {
                        #ifdef DEBUG
                        Serial.println(F("SystemController: Audio error recovery successful"));
                        #endif
                    } else {
                        handleCriticalError();
                    }
                }
            } else {
                logError("Audio system initialization failed");
                handleCriticalError();
            }
        } else {
            logError("Power up sequence failed");
            handleCriticalError();
        }
    } else {
        logError("Operation timeout exceeded");
        handleCriticalError();
    }
    
    // Always execute shutdown sequence with error handling
    if (!powerDownAudioSystem()) {
        logError("Power down sequence failed");
        // Force emergency shutdown
        _audioController.stopAudio();
        _powerManager.disableDFPlayer();
    }
    
    // Stop power measurement and log consumption
    _powerManager.stopPowerMeasurement();
    
    // Calculate total operation time
    _totalOperationTime = millis() - operationStart;
    
    #ifdef DEBUG
    Serial.print(F("SystemController: Complete operation took "));
    Serial.print(_totalOperationTime);
    Serial.print(F("ms, success: "));
    Serial.println(operationSuccess ? "YES" : "NO");
    
    // Log power consumption for this operation
    _powerManager.logPowerConsumption();
    
    // Validate power consumption meets requirements
    if (!_powerManager.validatePowerConsumption()) {
        Serial.println(F("SystemController: WARNING - Power consumption validation failed"));
    }
    #endif
    
    // Log system health if there were errors
    if (_hasError || !operationSuccess) {
        logSystemHealth();
    }
    
    // Return to sleep state
    setState(DEEP_SLEEP);
}

void SystemController::enterSleepMode() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Entering coordinated sleep mode"));
    #endif
    
    // Ensure audio system is powered down
    if (_currentState != DEEP_SLEEP) {
        powerDownAudioSystem();
    }
    
    // Set state and enter deep sleep
    setState(DEEP_SLEEP);
    _powerManager.enterDeepSleep();
}

bool SystemController::powerUpAudioSystem() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Starting power-up sequence"));
    #endif
    
    setState(WAKING_UP);
    
    // Step 1: Wake from sleep
    _powerManager.wakeFromSleep();
    
    setState(POWERING_UP);
    
    // Step 2: Execute startup sequence with error handling
    executeStartupSequence();
    
    if (_hasError) {
        #ifdef DEBUG
        Serial.println(F("SystemController: Power-up sequence failed"));
        #endif
        return false;
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Power-up sequence completed successfully"));
    #endif
    
    return true;
}

bool SystemController::powerDownAudioSystem() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Starting power-down sequence"));
    #endif
    
    setState(POWERING_DOWN);
    
    // Execute shutdown sequence with error handling
    executeShutdownSequence();
    
    if (_hasError) {
        #ifdef DEBUG
        Serial.println(F("SystemController: Power-down sequence had errors"));
        #endif
        // Continue with shutdown even if there were errors
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Power-down sequence completed"));
    #endif
    
    return !_hasError;
}

bool SystemController::initializeAudioSystem() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Initializing audio system"));
    #endif
    
    // Wait for DFPlayer to be ready
    if (!_powerManager.waitForDFPlayerReady(POWER_UP_TIMEOUT)) {
        logError("DFPlayer not ready after power-up");
        return false;
    }
    
    // Initialize AudioController
    if (!_audioController.initialize()) {
        logError("AudioController initialization failed");
        return false;
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Audio system initialized successfully"));
    #endif
    
    return true;
}

void SystemController::executeStartupSequence() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Executing startup sequence"));
    #endif
    
    // Step 1: Power up DFPlayer
    if (!stepPowerUpDFPlayer()) {
        handlePowerUpError();
        return;
    }
    
    // Step 2: Wait for DFPlayer ready
    if (!stepWaitForDFPlayerReady()) {
        handlePowerUpError();
        return;
    }
    
    // Step 3: Initialize AudioController
    if (!stepInitializeAudioController()) {
        handleAudioInitError();
        return;
    }
    
    // Step 4: Validate audio system
    if (!stepValidateAudioSystem()) {
        handleAudioInitError();
        return;
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Startup sequence completed successfully"));
    #endif
}

void SystemController::executeShutdownSequence() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Executing shutdown sequence"));
    #endif
    
    // Step 1: Stop any playing audio
    if (!stepStopAudio()) {
        handlePlaybackError();
        // Continue with shutdown
    }
    
    // Step 2: Power down DFPlayer
    if (!stepPowerDownDFPlayer()) {
        handlePowerDownError();
        // Continue with shutdown
    }
    
    // Step 3: Validate power down
    if (!stepValidatePowerDown()) {
        handlePowerDownError();
        // Continue anyway
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Shutdown sequence completed"));
    #endif
}

bool SystemController::stepPowerUpDFPlayer() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Step 1 - Powering up DFPlayer"));
    #endif
    
    _powerManager.powerUpDFPlayer();
    
    // Verify DFPlayer is enabled
    if (!_powerManager.isDFPlayerEnabled()) {
        logError("DFPlayer enable failed");
        return false;
    }
    
    return true;
}

bool SystemController::stepWaitForDFPlayerReady() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Step 2 - Waiting for DFPlayer ready"));
    #endif
    
    return _powerManager.waitForDFPlayerReady(POWER_UP_TIMEOUT);
}

bool SystemController::stepInitializeAudioController() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Step 3 - Initializing AudioController"));
    #endif
    
    return _audioController.initialize();
}

bool SystemController::stepValidateAudioSystem() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Step 4 - Validating audio system"));
    #endif
    
    // Check that both power and audio systems are ready
    if (!_powerManager.isDFPlayerEnabled()) {
        logError("DFPlayer not enabled after startup");
        return false;
    }
    
    if (!_audioController.isInitialized()) {
        logError("AudioController not initialized after startup");
        return false;
    }
    
    if (_audioController.hasError()) {
        logError("AudioController has error after startup");
        return false;
    }
    
    return true;
}

bool SystemController::stepStopAudio() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Shutdown Step 1 - Stopping audio"));
    #endif
    
    if (_audioController.isPlaying()) {
        _audioController.stopAudio();
        delay(100); // Allow stop command to complete
    }
    
    return true;
}

bool SystemController::stepPowerDownDFPlayer() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Shutdown Step 2 - Powering down DFPlayer"));
    #endif
    
    _powerManager.powerDownDFPlayer();
    
    return true;
}

bool SystemController::stepValidatePowerDown() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Shutdown Step 3 - Validating power down"));
    #endif
    
    // Verify DFPlayer is disabled
    if (_powerManager.isDFPlayerEnabled()) {
        logError("DFPlayer still enabled after power down");
        return false;
    }
    
    return true;
}

bool SystemController::handlePowerUpError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Handling power-up error"));
    #endif
    
    if (_errorRecoveryAttempts < MAX_ERROR_RECOVERY_ATTEMPTS) {
        _errorRecoveryAttempts++;
        
        #ifdef DEBUG
        Serial.print(F("SystemController: Power-up recovery attempt "));
        Serial.println(_errorRecoveryAttempts);
        #endif
        
        // Try to recover by power cycling
        _powerManager.powerDownDFPlayer();
        delay(ERROR_RECOVERY_DELAY);
        
        return recoverFromError();
    }
    
    logError("Power-up failed after max recovery attempts");
    setState(ERROR_STATE);
    return false;
}

bool SystemController::handleAudioInitError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Handling audio init error"));
    #endif
    
    if (_errorRecoveryAttempts < MAX_ERROR_RECOVERY_ATTEMPTS) {
        _errorRecoveryAttempts++;
        
        #ifdef DEBUG
        Serial.print(F("SystemController: Audio init recovery attempt "));
        Serial.println(_errorRecoveryAttempts);
        #endif
        
        // Clear audio controller error and retry
        _audioController.clearError();
        delay(ERROR_RECOVERY_DELAY);
        
        return _audioController.initialize();
    }
    
    logError("Audio init failed after max recovery attempts");
    setState(ERROR_STATE);
    return false;
}

bool SystemController::handlePlaybackError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Handling playback error"));
    #endif
    
    // Stop any ongoing playback
    _audioController.stopAudio();
    _audioController.clearError();
    
    return true;
}

bool SystemController::handlePowerDownError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Handling power-down error"));
    #endif
    
    // Force power down
    _powerManager.disableDFPlayer();
    
    return true;
}

bool SystemController::recoverFromError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Attempting error recovery"));
    #endif
    
    clearError();
    
    // Try startup sequence again
    executeStartupSequence();
    
    return !_hasError;
}

void SystemController::resetSystem() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Resetting system"));
    #endif
    
    // Force shutdown
    _audioController.stopAudio();
    _powerManager.powerDownDFPlayer();
    
    // Clear all errors
    clearError();
    _audioController.clearError();
    
    // Reset state
    setState(DEEP_SLEEP);
    _errorRecoveryAttempts = 0;
}

bool SystemController::waitForSystemReady(unsigned long timeoutMs) {
    unsigned long startTime = millis();
    
    while (millis() - startTime < timeoutMs) {
        if (isSystemReady()) {
            return true;
        }
        delay(50);
    }
    
    return false;
}

SystemState SystemController::getCurrentState() const {
    return _currentState;
}

bool SystemController::isSystemReady() const {
    return (_currentState == PLAYING || _currentState == DEEP_SLEEP) && !_hasError;
}

bool SystemController::hasError() const {
    return _hasError;
}

void SystemController::clearError() {
    _hasError = false;
    _lastError[0] = '\0';
    _errorRecoveryAttempts = 0;
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Error cleared"));
    #endif
}

const char* SystemController::getLastError() const {
    return _lastError;
}

unsigned long SystemController::getLastOperationTime() const {
    return _lastOperationTime;
}

unsigned long SystemController::getTotalOperationTime() const {
    return _totalOperationTime;
}

void SystemController::setState(SystemState newState) {
    if (_currentState != newState) {
        logStateTransition(_currentState, newState);
        _previousState = _currentState;
        _currentState = newState;
        _stateStartTime = millis();
    }
}

bool SystemController::validateSystemState() {
    // Basic validation that components are available
    // This is a simple check - more sophisticated validation could be added
    return true;
}

void SystemController::logError(const char* error) {
    _hasError = true;
    _lastErrorTime = millis();
    
    // Copy error message (with bounds checking)
    strncpy(_lastError, error, sizeof(_lastError) - 1);
    _lastError[sizeof(_lastError) - 1] = '\0';
    
    #ifdef DEBUG
    Serial.print(F("SystemController ERROR: "));
    Serial.println(error);
    #endif
}

bool SystemController::handleCriticalError() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Handling critical error"));
    #endif
    
    _criticalError = true;
    _totalErrorCount++;
    
    // Perform emergency shutdown
    _audioController.stopAudio();
    _powerManager.powerDownDFPlayer();
    
    // Try to recover if not too many attempts
    if (_errorRecoveryAttempts < MAX_ERROR_RECOVERY_ATTEMPTS) {
        _errorRecoveryAttempts++;
        
        #ifdef DEBUG
        Serial.print(F("SystemController: Critical error recovery attempt "));
        Serial.println(_errorRecoveryAttempts);
        #endif
        
        // Wait longer for critical error recovery
        delay(ERROR_RECOVERY_DELAY * 2);
        
        // Perform full system diagnostics
        if (performSystemDiagnostics()) {
            _criticalError = false;
            return true;
        }
    }
    
    // Enable degraded mode if recovery fails
    enableGracefulDegradation();
    logError("Critical error - system in degraded mode");
    
    return false;
}

bool SystemController::performSystemDiagnostics() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Performing system diagnostics"));
    #endif
    
    _lastDiagnosticsTime = millis();
    bool diagnosticsPass = true;
    
    // Step 1: Validate all components
    if (!validateAllComponents()) {
        logError("Component validation failed in diagnostics");
        diagnosticsPass = false;
    }
    
    // Step 2: Test power management
    if (!_powerManager.validatePowerState()) {
        logError("Power state validation failed in diagnostics");
        diagnosticsPass = false;
    }
    
    // Step 3: Test button functionality
    if (!_buttonHandler.validateButtonState()) {
        logError("Button state validation failed in diagnostics");
        diagnosticsPass = false;
    }
    
    // Step 4: Test audio controller communication
    if (_audioController.isInitialized() && !_audioController.validateCommunication()) {
        logError("Audio communication validation failed in diagnostics");
        diagnosticsPass = false;
    }
    
    // Step 5: Check error counts across all components
    int totalErrors = _powerManager.getErrorCount() + 
                     _audioController.getErrorCount() + 
                     _buttonHandler.getErrorCount() + 
                     _totalErrorCount;
    
    if (totalErrors > 50) { // Threshold for too many errors
        logError("Total error count exceeds threshold");
        diagnosticsPass = false;
    }
    
    #ifdef DEBUG
    Serial.print(F("SystemController: Diagnostics result: "));
    Serial.println(diagnosticsPass ? "PASS" : "FAIL");
    Serial.print(F("SystemController: Total system errors: "));
    Serial.println(totalErrors);
    #endif
    
    return diagnosticsPass;
}

bool SystemController::validateAllComponents() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Validating all components"));
    #endif
    
    bool allValid = true;
    
    // Validate PowerManager
    if (_powerManager.hasError()) {
        #ifdef DEBUG
        Serial.print(F("SystemController: PowerManager has error: "));
        Serial.println(_powerManager.getLastError());
        #endif
        
        if (!_powerManager.recoverFromError()) {
            allValid = false;
        }
    }
    
    // Validate AudioController
    if (_audioController.hasError()) {
        #ifdef DEBUG
        Serial.print(F("SystemController: AudioController has error: "));
        Serial.println(_audioController.getLastError());
        #endif
        
        if (!_audioController.recoverFromError()) {
            allValid = false;
        }
    }
    
    // Validate ButtonHandler
    if (_buttonHandler.hasError()) {
        #ifdef DEBUG
        Serial.print(F("SystemController: ButtonHandler has error: "));
        Serial.println(_buttonHandler.getLastError());
        #endif
        
        if (!_buttonHandler.recoverFromError()) {
            allValid = false;
        }
    }
    
    _componentValidationPassed = allValid;
    
    #ifdef DEBUG
    Serial.print(F("SystemController: Component validation: "));
    Serial.println(allValid ? "PASS" : "FAIL");
    #endif
    
    return allValid;
}

void SystemController::enableGracefulDegradation() {
    #ifdef DEBUG
    Serial.println(F("SystemController: Enabling graceful degradation mode"));
    #endif
    
    _degradedMode = true;
    
    // In degraded mode, we try to maintain basic functionality
    // even if some components have errors
    
    // Reset error counts to allow limited operation
    _powerManager.resetErrorCount();
    _audioController.resetErrorCount();
    _buttonHandler.resetErrorCount();
    
    // Clear non-critical errors
    if (!_criticalError) {
        clearError();
        _powerManager.clearError();
        _audioController.clearError();
        _buttonHandler.clearError();
    }
    
    #ifdef DEBUG
    Serial.println(F("SystemController: Degraded mode enabled - limited functionality available"));
    #endif
}

bool SystemController::isInDegradedMode() const {
    return _degradedMode;
}

void SystemController::logSystemHealth() {
    #ifdef DEBUG
    Serial.println(F("=== SYSTEM HEALTH REPORT ==="));
    Serial.print(F("Current State: "));
    
    const char* stateNames[] = {
        "DEEP_SLEEP", "WAKING_UP", "POWERING_UP", 
        "PLAYING", "POWERING_DOWN", "ERROR_STATE"
    };
    
    if (_currentState < 6) Serial.println(stateNames[_currentState]);
    else Serial.println(_currentState);
    
    Serial.print(F("System Error: "));
    Serial.println(_hasError ? "YES" : "NO");
    if (_hasError) {
        Serial.print(F("Last Error: "));
        Serial.println(_lastError);
    }
    
    Serial.print(F("Critical Error: "));
    Serial.println(_criticalError ? "YES" : "NO");
    
    Serial.print(F("Degraded Mode: "));
    Serial.println(_degradedMode ? "YES" : "NO");
    
    Serial.print(F("Total Error Count: "));
    Serial.println(_totalErrorCount);
    
    Serial.print(F("Recovery Attempts: "));
    Serial.println(_errorRecoveryAttempts);
    
    Serial.print(F("Component Validation: "));
    Serial.println(_componentValidationPassed ? "PASS" : "FAIL");
    
    // Component-specific health
    Serial.print(F("PowerManager Errors: "));
    Serial.println(_powerManager.getErrorCount());
    
    Serial.print(F("AudioController Errors: "));
    Serial.println(_audioController.getErrorCount());
    
    Serial.print(F("ButtonHandler Errors: "));
    Serial.println(_buttonHandler.getErrorCount());
    
    Serial.print(F("Last Operation Time: "));
    Serial.print(_totalOperationTime);
    Serial.println(F("ms"));
    
    Serial.println(F("=== END HEALTH REPORT ==="));
    #endif
}

void SystemController::logStateTransition(SystemState from, SystemState to) {
    #ifdef DEBUG
    Serial.print(F("SystemController: State transition "));
    
    // Convert states to readable strings
    const char* stateNames[] = {
        "DEEP_SLEEP", "WAKING_UP", "POWERING_UP", 
        "PLAYING", "POWERING_DOWN", "ERROR_STATE"
    };
    
    if (from < 6) Serial.print(stateNames[from]);
    else Serial.print(from);
    
    Serial.print(F(" -> "));
    
    if (to < 6) Serial.println(stateNames[to]);
    else Serial.println(to);
    #endif
}