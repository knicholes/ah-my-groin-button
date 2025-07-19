#ifndef BUTTON_HANDLER_H
#define BUTTON_HANDLER_H

#include <Arduino.h>

/**
 * ButtonHandler Class
 * 
 * Manages button input with interrupt-based detection and software debouncing.
 * Provides reliable button press detection for the audio trigger system.
 * 
 * Key Features:
 * - Interrupt-driven button detection for wake-up capability
 * - Software debouncing to prevent multiple triggers
 * - Button state management and change detection
 * - Support for both press and release detection
 * 
 * Requirements addressed: 4.1, 4.2, 4.3, 4.4
 */
class ButtonHandler {
public:
    // Constructor
    ButtonHandler(int buttonPin = 2, unsigned long debounceDelay = 50);
    
    // Initialization
    void begin();
    
    // Button state management
    bool isPressed();
    bool wasPressed();
    bool wasReleased();
    bool stateChanged();
    
    // Debouncing and state updates
    void update();
    void reset();
    
    // Interrupt management
    void setupInterrupt();
    void enableInterrupt();
    void disableInterrupt();
    
    // Configuration
    void setDebounceDelay(unsigned long delay);
    unsigned long getDebounceDelay() const;
    
    // State information
    unsigned long getLastPressTime() const;
    unsigned long getLastReleaseTime() const;
    unsigned long getPressCount() const;
    
    // Enhanced error handling and recovery
    bool hasError() const;
    void clearError();
    const char* getLastError() const;
    bool recoverFromError();
    bool validateButtonState();
    int getErrorCount() const;
    void resetErrorCount();
    
    // Static interrupt handler
    static void interruptHandler();
    
private:
    // Pin configuration
    int _buttonPin;
    
    // Debouncing parameters
    unsigned long _debounceDelay;
    unsigned long _lastDebounceTime;
    
    // Button state tracking
    bool _currentState;
    bool _previousState;
    bool _debouncedState;
    bool _lastDebouncedState;
    bool _stateChanged;
    bool _wasPressed;
    bool _wasReleased;
    
    // Timing information
    unsigned long _lastPressTime;
    unsigned long _lastReleaseTime;
    unsigned long _pressCount;
    
    // Enhanced error tracking
    bool _hasError;
    char _lastError[64];
    int _errorCount;
    unsigned long _lastErrorTime;
    
    // Interrupt flag
    static volatile bool _interruptTriggered;
    static ButtonHandler* _instance;
    
    // Private methods
    bool readButtonState();
    void updateButtonState();
    void handleStateChange();
    void logError(const char* error);
};

// Global instance declaration (defined in ButtonHandler.cpp)
extern ButtonHandler buttonHandler;

#endif // BUTTON_HANDLER_H