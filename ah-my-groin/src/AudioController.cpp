#include "AudioController.h"

AudioController::AudioController(SoftwareSerial& serial, int volume)
    : _serial(&serial)
    , _volume(volume)
    , _initialized(false)
    , _playing(false)
    , _hasError(false)
    , _playStartTime(0)
    , _errorCount(0)
    , _lastErrorTime(0)
    , _sdCardPresent(false)
    , _communicationValid(false)
{
    // Constructor - initialization happens in initialize()
    _lastError[0] = '\0';
}

bool AudioController::initialize() {
    #ifdef DEBUG
    Serial.println(F("AudioController: Initializing DFPlayer..."));
    #endif
    
    _hasError = false;
    _initialized = false;
    
    // Attempt initialization with retries
    for (int attempt = 0; attempt < MAX_INIT_RETRIES; attempt++) {
        #ifdef DEBUG
        Serial.print(F("AudioController: Initialization attempt "));
        Serial.print(attempt + 1);
        Serial.print(F(" of "));
        Serial.println(MAX_INIT_RETRIES);
        #endif
        
        if (attemptInitialization()) {
            _initialized = true;
            configurePlayer();
            
            #ifdef DEBUG
            Serial.println(F("AudioController: DFPlayer initialized successfully"));
            #endif
            return true;
        }
        
        // Wait before retry
        if (attempt < MAX_INIT_RETRIES - 1) {
            delay(500);
        }
    }
    
    #ifdef DEBUG
    Serial.println(F("AudioController: DFPlayer initialization failed after all attempts"));
    #endif
    
    logError("DFPlayer initialization failed after all retries");
    return false;
}

bool AudioController::attemptInitialization() {
    unsigned long startTime = millis();
    
    // Try standard initialization first
    while (millis() - startTime < INIT_TIMEOUT) {
        if (_dfPlayer.begin(*_serial, false, false)) {
            return true;
        }
        delay(100);
    }
    
    // Try with reset if standard method failed
    startTime = millis();
    while (millis() - startTime < INIT_TIMEOUT) {
        if (_dfPlayer.begin(*_serial, false, true)) {
            return true;
        }
        delay(100);
    }
    
    return false;
}

void AudioController::configurePlayer() {
    // Set volume
    _dfPlayer.volume(_volume);
    delay(COMMAND_DELAY);
    
    // Set EQ to normal
    _dfPlayer.EQ(DFPLAYER_EQ_NORMAL);
    delay(COMMAND_DELAY);
    
    #ifdef DEBUG
    Serial.print(F("AudioController: Volume set to "));
    Serial.println(_volume);
    #endif
}

bool AudioController::playAudio(int trackNumber) {
    if (!_initialized) {
        logError("Cannot play - not initialized");
        return false;
    }
    
    // Check for too many errors
    if (_errorCount >= MAX_ERROR_COUNT) {
        logError("Too many errors - playback disabled");
        return false;
    }
    
    // Validate communication before attempting playback
    if (!validateCommunication()) {
        logError("Communication validation failed before playback");
        return false;
    }
    
    // Stop any current playback with timeout protection
    if (_playing) {
        unsigned long stopStart = millis();
        stopAudio();
        delay(100);
        
        // Verify stop completed within reasonable time
        if (millis() - stopStart > 1000) {
            logError("Stop audio timeout");
        }
    }
    
    #ifdef DEBUG
    Serial.print(F("AudioController: Playing track "));
    Serial.println(trackNumber);
    #endif
    
    // Start playback with error handling
    unsigned long playStart = millis();
    _dfPlayer.play(trackNumber);
    _playing = true;
    _playStartTime = millis();
    
    // Brief validation that play command was accepted
    delay(100);
    if (millis() - playStart > 500) {
        logError("Play command timeout");
        return false;
    }
    
    return true;
}

void AudioController::stopAudio() {
    if (_playing) {
        #ifdef DEBUG
        Serial.println(F("AudioController: Stopping audio"));
        #endif
        
        _dfPlayer.stop();
        _playing = false;
        _playStartTime = 0;
    }
}

bool AudioController::isPlaying() {
    if (!_playing) {
        return false;
    }
    
    // Check for completion status from DFPlayer
    if (checkPlaybackStatus()) {
        return _playing;
    }
    
    return _playing;
}

bool AudioController::waitForCompletion(unsigned long timeoutMs) {
    if (!_playing) {
        #ifdef DEBUG
        Serial.println(F("AudioController: No audio playing"));
        #endif
        return true;
    }
    
    #ifdef DEBUG
    Serial.print(F("AudioController: Waiting for completion (timeout: "));
    Serial.print(timeoutMs);
    Serial.println(F("ms)"));
    #endif
    
    unsigned long startTime = millis();
    bool completed = false;
    
    while (millis() - startTime < timeoutMs && _playing) {
        // Check for DFPlayer status messages
        if (checkPlaybackStatus()) {
            if (!_playing) {
                completed = true;
                break;
            }
        }
        
        delay(50);
    }
    
    if (!completed && _playing) {
        #ifdef DEBUG
        Serial.println(F("AudioController: Playback timeout - forcing stop"));
        #endif
        stopAudio();
        return false; // Timeout occurred
    }
    
    #ifdef DEBUG
    Serial.println(F("AudioController: Playback completed"));
    #endif
    return true;
}

bool AudioController::checkPlaybackStatus() {
    if (!_initialized) {
        return false;
    }
    
    // Check for DFPlayer messages
    if (_dfPlayer.available()) {
        uint8_t type = _dfPlayer.readType();
        #ifdef DEBUG
        int value = _dfPlayer.read();  // Moved inside DEBUG
        #else
        (void)_dfPlayer.read();  // Discard value when not debugging
        #endif
        
        #ifdef DEBUG
        Serial.print(F("AudioController: DFPlayer message - Type: "));
        Serial.print(type);
        Serial.print(F(", Value: "));
        Serial.println(value);
        #endif
        
        switch (type) {
            case DFPlayerPlayFinished:
                #ifdef DEBUG
                Serial.println(F("AudioController: Playback finished"));
                #endif
                _playing = false;
                _playStartTime = 0;
                return true;
                
            case DFPlayerError:
                #ifdef DEBUG
                Serial.print(F("AudioController: DFPlayer error: "));
                Serial.println(value);
                #endif
                _hasError = true;
                _playing = false;
                _playStartTime = 0;
                return true;
                
            case DFPlayerCardInserted:
                #ifdef DEBUG
                Serial.println(F("AudioController: SD card inserted"));
                #endif
                break;
                
            case DFPlayerCardRemoved:
                #ifdef DEBUG
                Serial.println(F("AudioController: SD card removed"));
                #endif
                _hasError = true;
                _playing = false;
                break;
        }
    }
    
    return false;
}

void AudioController::setVolume(int volume) {
    if (volume < 0) volume = 0;
    if (volume > 30) volume = 30;
    
    _volume = volume;
    
    if (_initialized) {
        _dfPlayer.volume(_volume);
        delay(COMMAND_DELAY);
        
        #ifdef DEBUG
        Serial.print(F("AudioController: Volume changed to "));
        Serial.println(_volume);
        #endif
    }
}

int AudioController::getVolume() const {
    return _volume;
}

bool AudioController::isInitialized() const {
    return _initialized;
}

bool AudioController::hasError() const {
    return _hasError;
}

void AudioController::clearError() {
    _hasError = false;
    
    #ifdef DEBUG
    Serial.println(F("AudioController: Error cleared"));
    #endif
}

bool AudioController::recoverFromError() {
    #ifdef DEBUG
    Serial.println(F("AudioController: Attempting error recovery"));
    #endif
    
    if (_errorCount >= MAX_ERROR_COUNT) {
        logError("Max error count reached - recovery disabled");
        return false;
    }
    
    // Clear current error state
    clearError();
    _communicationValid = false;
    _sdCardPresent = false;
    
    // Attempt to re-initialize with timeout protection
    unsigned long recoveryStart = millis();
    bool recovered = false;
    
    // Step 1: Validate communication
    if (validateCommunication()) {
        #ifdef DEBUG
        Serial.println(F("AudioController: Communication validated"));
        #endif
        
        // Step 2: Check SD card
        if (checkSDCard()) {
            #ifdef DEBUG
            Serial.println(F("AudioController: SD card validated"));
            #endif
            
            // Step 3: Re-initialize if needed
            if (!_initialized) {
                recovered = initialize();
            } else {
                // Just reconfigure if already initialized
                configurePlayer();
                recovered = true;
            }
        } else {
            logError("SD card check failed during recovery");
        }
    } else {
        logError("Communication validation failed during recovery");
    }
    
    #ifdef DEBUG
    unsigned long recoveryTime = millis() - recoveryStart;  // Moved inside DEBUG
    Serial.print(F("AudioController: Recovery attempt took "));
    Serial.print(recoveryTime);
    Serial.print(F("ms, result: "));
    Serial.println(recovered ? "SUCCESS" : "FAILED");
    #endif
    
    if (!recovered) {
        _errorCount++;
        _lastErrorTime = millis();
    }
    
    return recovered;
}

bool AudioController::validateCommunication() {
    #ifdef DEBUG
    Serial.println(F("AudioController: Validating DFPlayer communication"));
    #endif
    
    if (!_initialized) {
        return false;
    }
    
    unsigned long startTime = millis();
    bool communicationOk = false;
    
    // Try to get volume as a communication test
    while (millis() - startTime < COMMUNICATION_TIMEOUT) {
        // Send a simple query command
        _dfPlayer.volume(_volume);
        delay(COMMAND_DELAY);
        
        // Check for any response or error
        if (checkPlaybackStatus() || !_hasError) {
            communicationOk = true;
            break;
        }
        
        delay(100);
    }
    
    _communicationValid = communicationOk;
    
    if (!communicationOk) {
        logError("DFPlayer communication timeout");
    }
    
    #ifdef DEBUG
    Serial.print(F("AudioController: Communication validation: "));
    Serial.println(communicationOk ? "PASS" : "FAIL");
    #endif
    
    return communicationOk;
}

bool AudioController::checkSDCard() {
    #ifdef DEBUG
    Serial.println(F("AudioController: Checking SD card presence"));
    #endif
    
    if (!_initialized) {
        return false;
    }
    
    unsigned long startTime = millis();
    bool sdCardOk = false;
    
    // Try to query file count or play a file to test SD card
    while (millis() - startTime < SD_CHECK_TIMEOUT) {
        // Clear any previous errors
        while (_dfPlayer.available()) {
            _dfPlayer.readType();
            _dfPlayer.read();
        }
        
        // Try to read file count (this will fail if no SD card)
        _dfPlayer.readFileCounts();
        delay(200);
        
        // Check for response
        bool gotResponse = false;
        unsigned long responseStart = millis();
        while (millis() - responseStart < 500) {
            if (_dfPlayer.available()) {
                uint8_t type = _dfPlayer.readType();
                (void)_dfPlayer.read(); // Read value but don't use it - cast to void to suppress warning
                
                if (type == DFPlayerCardRemoved) {
                    logError("SD card removed");
                    return false;
                } else if (type != DFPlayerError) {
                    gotResponse = true;
                    sdCardOk = true;
                    break;
                }
            }
            delay(10);
        }
        
        if (gotResponse) {
            break;
        }
        
        delay(100);
    }
    
    _sdCardPresent = sdCardOk;
    
    if (!sdCardOk) {
        logError("SD card not detected or not responding");
    }
    
    #ifdef DEBUG
    Serial.print(F("AudioController: SD card check: "));
    Serial.println(sdCardOk ? "PASS" : "FAIL");
    #endif
    
    return sdCardOk;
}

const char* AudioController::getLastError() const {
    return _lastError;
}

int AudioController::getErrorCount() const {
    return _errorCount;
}

void AudioController::resetErrorCount() {
    _errorCount = 0;
    _lastErrorTime = 0;
    
    #ifdef DEBUG
    Serial.println(F("AudioController: Error count reset"));
    #endif
}

void AudioController::logError(const char* error) {
    _hasError = true;
    _errorCount++;
    _lastErrorTime = millis();
    
    // Copy error message with bounds checking
    strncpy(_lastError, error, sizeof(_lastError) - 1);
    _lastError[sizeof(_lastError) - 1] = '\0';
    
    #ifdef DEBUG
    Serial.print(F("AudioController ERROR: "));
    Serial.println(error);
    Serial.print(F("AudioController: Error count: "));
    Serial.println(_errorCount);
    #endif
}