#ifndef AUDIO_CONTROLLER_H
#define AUDIO_CONTROLLER_H

#include <Arduino.h>
#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>

/**
 * AudioController Class
 * 
 * Manages trigger-based audio playback for the button-triggered audio device.
 * Provides single-play functionality with proper completion detection.
 * 
 * Key Features:
 * - Single audio playback per trigger
 * - Audio completion detection
 * - Proper DFPlayer initialization and communication
 * - Error handling and recovery
 */
class AudioController {
public:
    // Constructor
    AudioController(SoftwareSerial& serial, int volume = 15);
    
    // Initialization
    bool initialize();
    
    // Audio playback control
    bool playAudio(int trackNumber = 1);
    void stopAudio();
    bool isPlaying();
    
    // Audio completion detection
    bool waitForCompletion(unsigned long timeoutMs = 5000);
    
    // Configuration
    void setVolume(int volume);
    int getVolume() const;
    
    // Status and error handling
    bool isInitialized() const;
    bool hasError() const;
    void clearError();
    
    // Enhanced error handling and recovery
    bool recoverFromError();
    bool validateCommunication();
    bool checkSDCard();
    const char* getLastError() const;
    int getErrorCount() const;
    void resetErrorCount();
    
private:
    // DFPlayer communication
    SoftwareSerial* _serial;
    DFRobotDFPlayerMini _dfPlayer;
    
    // Configuration
    int _volume;
    
    // State tracking
    bool _initialized;
    bool _playing;
    bool _hasError;
    unsigned long _playStartTime;
    
    // Enhanced error tracking
    char _lastError[64];
    int _errorCount;
    unsigned long _lastErrorTime;
    bool _sdCardPresent;
    bool _communicationValid;
    
    // Constants
    static const unsigned long INIT_TIMEOUT = 3000;
    static const unsigned long COMMAND_DELAY = 100;
    static const int MAX_INIT_RETRIES = 3;
    static const unsigned long COMMUNICATION_TIMEOUT = 1000;
    static const unsigned long SD_CHECK_TIMEOUT = 2000;
    static const int MAX_ERROR_COUNT = 10;
    
    // Private methods
    bool attemptInitialization();
    void configurePlayer();
    bool checkPlaybackStatus();
    void logError(const char* error);
};

#endif // AUDIO_CONTROLLER_H