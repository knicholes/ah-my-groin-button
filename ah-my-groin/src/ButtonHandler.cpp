#include "ButtonHandler.h"

// Static member definitions
volatile bool ButtonHandler::_interruptTriggered = false;
ButtonHandler* ButtonHandler::_instance = nullptr;

// Global instance
ButtonHandler buttonHandler;

ButtonHandler::ButtonHandler(int buttonPin, unsigned long debounceDelay)
    : _buttonPin(buttonPin)
    , _debounceDelay(debounceDelay)
    , _lastDebounceTime(0)
    , _currentState(false)
    , _previousState(false)
    , _debouncedState(false)
    , _lastDebouncedState(false)
    , _stateChanged(false)
    , _wasPressed(false)
    , _wasReleased(false)
    , _lastPressTime(0)
    , _lastReleaseTime(0)
    , _pressCount(0)
    , _hasError(false)
    , _errorCount(0)
    , _lastErrorTime(0)
{
    _instance = this;
    _lastError[0] = '\0';
}

void ButtonHandler::begin() {
    // Clear any previous errors
    clearError();
    
    // Validate button state before initialization
    if (!validateButtonState()) {
        logError("Button validation failed during initialization");
        return;
    }
    
    // Configure button pin with internal pull-up resistor
    // Button connects between pin and GND (active LOW)
    pinMode(_buttonPin, INPUT_PULLUP);
    
    // Initialize button state with timeout protection
    unsigned long initStart = millis();
    _currentState = readButtonState();
    _previousState = _currentState;
    _debouncedState = _currentState;
    _lastDebouncedState = _currentState;
    
    // Reset state flags
    _stateChanged = false;
    _wasPressed = false;
    _wasReleased = false;
    
    // Setup interrupt for wake-up capability
    setupInterrupt();
    
    // Verify initialization completed within reasonable time
    if (millis() - initStart > 1000) {
        logError("Button initialization timeout");
    }
}

bool ButtonHandler::readButtonState() {
    // Button is active LOW (pressed = LOW, released = HIGH)
    // Return true when button is pressed (pin reads LOW)
    return digitalRead(_buttonPin) == LOW;
}

void ButtonHandler::update() {
    // Read current button state
    _currentState = readButtonState();
    
    // Check if interrupt was triggered
    if (_interruptTriggered) {
        _interruptTriggered = false;
        // Force immediate state update on interrupt
        updateButtonState();
        return;
    }
    
    // Check if state has changed
    if (_currentState != _previousState) {
        // Reset debounce timer on state change
        _lastDebounceTime = millis();
    }
    
    // Update debounced state if enough time has passed
    if ((millis() - _lastDebounceTime) > _debounceDelay) {
        updateButtonState();
    }
    
    _previousState = _currentState;
}

void ButtonHandler::updateButtonState() {
    // Update debounced state
    _lastDebouncedState = _debouncedState;
    _debouncedState = _currentState;
    
    // Check for state changes
    _stateChanged = (_debouncedState != _lastDebouncedState);
    
    if (_stateChanged) {
        handleStateChange();
    } else {
        // Clear single-shot flags if no state change
        _wasPressed = false;
        _wasReleased = false;
    }
}

void ButtonHandler::handleStateChange() {
    unsigned long currentTime = millis();
    
    if (_debouncedState && !_lastDebouncedState) {
        // Button was pressed (LOW state = pressed)
        _wasPressed = true;
        _wasReleased = false;
        _lastPressTime = currentTime;
        _pressCount++;
    } else if (!_debouncedState && _lastDebouncedState) {
        // Button was released (HIGH state = released)
        _wasPressed = false;
        _wasReleased = true;
        _lastReleaseTime = currentTime;
    }
}

bool ButtonHandler::isPressed() {
    return _debouncedState;
}

bool ButtonHandler::wasPressed() {
    bool result = _wasPressed;
    _wasPressed = false; // Clear flag after reading (single-shot)
    return result;
}

bool ButtonHandler::wasReleased() {
    bool result = _wasReleased;
    _wasReleased = false; // Clear flag after reading (single-shot)
    return result;
}

bool ButtonHandler::stateChanged() {
    bool result = _stateChanged;
    _stateChanged = false; // Clear flag after reading (single-shot)
    return result;
}

void ButtonHandler::reset() {
    // Reset all state tracking
    _currentState = readButtonState();
    _previousState = _currentState;
    _debouncedState = _currentState;
    _lastDebouncedState = _currentState;
    
    _stateChanged = false;
    _wasPressed = false;
    _wasReleased = false;
    
    _lastDebounceTime = millis();
    _pressCount = 0;
}

void ButtonHandler::setupInterrupt() {
    // Attach interrupt for button pin (Pin 2 = INT0)
    // Trigger on FALLING edge (button press)
    attachInterrupt(digitalPinToInterrupt(_buttonPin), interruptHandler, FALLING);
}

void ButtonHandler::enableInterrupt() {
    attachInterrupt(digitalPinToInterrupt(_buttonPin), interruptHandler, FALLING);
}

void ButtonHandler::disableInterrupt() {
    detachInterrupt(digitalPinToInterrupt(_buttonPin));
}

void ButtonHandler::setDebounceDelay(unsigned long delay) {
    _debounceDelay = delay;
}

unsigned long ButtonHandler::getDebounceDelay() const {
    return _debounceDelay;
}

unsigned long ButtonHandler::getLastPressTime() const {
    return _lastPressTime;
}

unsigned long ButtonHandler::getLastReleaseTime() const {
    return _lastReleaseTime;
}

unsigned long ButtonHandler::getPressCount() const {
    return _pressCount;
}

bool ButtonHandler::hasError() const {
    return _hasError;
}

void ButtonHandler::clearError() {
    _hasError = false;
    _lastError[0] = '\0';
    
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Error cleared"));
    #endif
}

const char* ButtonHandler::getLastError() const {
    return _lastError;
}

bool ButtonHandler::recoverFromError() {
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Attempting error recovery"));
    #endif
    
    if (_errorCount >= 10) { // Max error threshold
        logError("Max error count reached - recovery disabled");
        return false;
    }
    
    // Clear current error state
    clearError();
    
    // Step 1: Validate button state
    if (!validateButtonState()) {
        logError("Button state validation failed during recovery");
        return false;
    }
    
    // Step 2: Reset button configuration
    pinMode(_buttonPin, INPUT_PULLUP);
    
    // Step 3: Reset interrupt
    disableInterrupt();
    delay(100);
    setupInterrupt();
    
    // Step 4: Reset state tracking
    reset();
    
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Error recovery completed"));
    #endif
    
    return true;
}

bool ButtonHandler::validateButtonState() {
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Validating button state"));
    #endif
    
    // Check pin configuration
    pinMode(_buttonPin, INPUT_PULLUP); // Ensure pin is configured correctly
    
    // Test button reading multiple times to ensure consistency
    bool readings[5];
    for (int i = 0; i < 5; i++) {
        readings[i] = digitalRead(_buttonPin);
        delay(10);
    }
    
    // Check for stuck button (all readings the same for extended period)
    bool allSame = true;
    for (int i = 1; i < 5; i++) {
        if (readings[i] != readings[0]) {
            allSame = false;
            break;
        }
    }
    
    // If button appears stuck in pressed state, this might indicate hardware issue
    if (allSame && readings[0] == LOW) {
        // Check if button has been stuck for too long
        unsigned long currentTime = millis();
        if (_lastPressTime > 0 && (currentTime - _lastPressTime) > 30000) { // 30 seconds
            logError("Button appears stuck in pressed state");
            return false;
        }
    }
    
    // Check interrupt functionality by testing pin interrupt capability
    int interruptPin = digitalPinToInterrupt(_buttonPin);
    if (interruptPin == NOT_AN_INTERRUPT) {
        logError("Button pin does not support interrupts");
        return false;
    }
    
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Button state validation passed"));
    #endif
    
    return true;
}

int ButtonHandler::getErrorCount() const {
    return _errorCount;
}

void ButtonHandler::resetErrorCount() {
    _errorCount = 0;
    _lastErrorTime = 0;
    
    #ifdef DEBUG
    Serial.println(F("ButtonHandler: Error count reset"));
    #endif
}

void ButtonHandler::logError(const char* error) {
    _hasError = true;
    _errorCount++;
    _lastErrorTime = millis();
    
    // Copy error message with bounds checking
    strncpy(_lastError, error, sizeof(_lastError) - 1);
    _lastError[sizeof(_lastError) - 1] = '\0';
    
    #ifdef DEBUG
    Serial.print(F("ButtonHandler ERROR: "));
    Serial.println(error);
    Serial.print(F("ButtonHandler: Error count: "));
    Serial.println(_errorCount);
    #endif
}

// Static interrupt handler
void ButtonHandler::interruptHandler() {
    // Keep ISR minimal and fast
    // Just set flag for main loop processing
    _interruptTriggered = true;
}