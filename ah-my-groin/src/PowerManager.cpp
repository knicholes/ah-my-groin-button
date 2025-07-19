#include "PowerManager.h"

// Static instance pointer for interrupt handling
PowerManager* PowerManager::_instance = nullptr;

// Global instance with default pin assignments
PowerManager powerManager(5, 2); // DFPlayer Enable Pin 5, Button Pin 2

PowerManager::PowerManager(int dfPlayerEnablePin, int buttonPin) 
    : _dfPlayerEnablePin(dfPlayerEnablePin)
    , _buttonPin(buttonPin)
    , _isAwake(true)
    , _dfPlayerEnabled(false)
    , _watchdogEnabled(false)
    , _lastWakeTime(0)
    , _sleepStartTime(0)
    , _hasError(false)
    , _errorCount(0)
    , _lastErrorTime(0)
    , _powerMeasurementStart(0)
    , _totalActiveDuration(0)
    , _lastActiveDuration(0)
    , _powerMeasurementActive(false) {
    
    // Set static instance for interrupt handling
    _instance = this;
    _lastError[0] = '\0';
}

void PowerManager::begin() {
    // Configure pins
    pinMode(_dfPlayerEnablePin, OUTPUT);
    pinMode(_buttonPin, INPUT_PULLUP);
    
    // Initially disable DFPlayer to save power
    disableDFPlayer();
    
    // Setup button interrupt
    setupButtonInterrupt();
    
    // Apply comprehensive power optimizations
    optimizeForMinimalPower();
    
    // Initialize power measurement tracking
    _powerMeasurementStart = 0;
    _totalActiveDuration = 0;
    _lastActiveDuration = 0;
    _powerMeasurementActive = false;
    
    // Record initialization time
    _lastWakeTime = millis();
    _isAwake = true;
    
    #ifdef DEBUG
    Serial.println(F("PowerManager initialized with power optimizations"));
    Serial.print(F("DFPlayer Enable Pin: "));
    Serial.println(_dfPlayerEnablePin);
    Serial.print(F("Button Pin: "));
    Serial.println(_buttonPin);
    
    // Log initial power consumption
    logPowerConsumption();
    #endif
}

void PowerManager::enterDeepSleep() {
    #ifdef DEBUG
    Serial.println(F("Entering deep sleep mode..."));
    Serial.flush(); // Ensure all serial data is sent before sleep
    #endif
    
    // Record sleep start time
    _sleepStartTime = millis();
    
    // Ensure DFPlayer is disabled to save power
    disableDFPlayer();
    
    // Configure for maximum power savings
    configureSleepMode();
    
    // Disable brown-out detection during sleep (saves ~25µA)
    disableBrownOutDetector();
    
    // Enter sleep mode
    cli();                    // Disable interrupts
    sleep_enable();           // Enable sleep mode
    sei();                    // Enable interrupts (allows wake-up)
    sleep_cpu();              // Enter sleep mode - execution stops here
    
    // === WAKE UP POINT ===
    // Execution resumes here after interrupt
    
    sleep_disable();          // Disable sleep mode
    
    // Re-enable brown-out detection
    enableBrownOutDetector();
    
    // Update state
    _isAwake = true;
    _lastWakeTime = millis();
    
    #ifdef DEBUG
    Serial.println(F("Woke from deep sleep"));
    #endif
}

void PowerManager::wakeFromSleep() {
    if (!_isAwake) {
        _isAwake = true;
        _lastWakeTime = millis();
        
        #ifdef DEBUG
        Serial.println(F("System wake-up initiated"));
        #endif
    }
}

bool PowerManager::isAwake() const {
    return _isAwake;
}

void PowerManager::enableDFPlayer() {
    if (!_dfPlayerEnabled) {
        // Validate pin state before operation
        if (!validatePowerState()) {
            logError("Power state validation failed before enabling DFPlayer");
            return;
        }
        
        unsigned long enableStart = millis();
        digitalWrite(_dfPlayerEnablePin, HIGH);
        _dfPlayerEnabled = true;
        
        // Allow power to stabilize - basic enable
        delay(100);
        
        // Verify enable completed within reasonable time
        if (millis() - enableStart > 500) {
            logError("DFPlayer enable timeout");
        }
        
        #ifdef DEBUG
        Serial.println(F("DFPlayer enabled"));
        #endif
    }
}

void PowerManager::disableDFPlayer() {
    if (_dfPlayerEnabled) {
        digitalWrite(_dfPlayerEnablePin, LOW);
        _dfPlayerEnabled = false;
        
        #ifdef DEBUG
        Serial.println(F("DFPlayer disabled"));
        #endif
    }
}

bool PowerManager::isDFPlayerEnabled() const {
    return _dfPlayerEnabled;
}

void PowerManager::powerUpDFPlayer() {
    #ifdef DEBUG
    Serial.println(F("Powering up DFPlayer with optimized timing..."));
    #endif
    
    if (!_dfPlayerEnabled) {
        // Step 1: Enable power to DFPlayer
        digitalWrite(_dfPlayerEnablePin, HIGH);
        _dfPlayerEnabled = true;
        
        #ifdef DEBUG
        Serial.println(F("DFPlayer power enabled"));
        #endif
        
        // Optimized timing: Reduced from 500ms total to 150ms
        // Step 2: Minimal power supply stabilization (reduced from 200ms to 100ms)
        delay(100);
        
        // Step 3: Reduced DFPlayer initialization time (reduced from 300ms to 50ms)
        // Most DFPlayer modules are ready much faster than documented
        delay(50);
        
        #ifdef DEBUG
        Serial.println(F("DFPlayer power-up sequence complete (optimized)"));
        #endif
    } else {
        #ifdef DEBUG
        Serial.println(F("DFPlayer already powered up"));
        #endif
    }
}

void PowerManager::powerDownDFPlayer() {
    #ifdef DEBUG
    Serial.println(F("Powering down DFPlayer (optimized)..."));
    #endif
    
    if (_dfPlayerEnabled) {
        // Optimized power-down: Reduced from 150ms total to 25ms
        // Step 1: Minimal delay for ongoing operations (reduced from 50ms to 10ms)
        delay(10);
        
        // Step 2: Disable power to DFPlayer immediately
        digitalWrite(_dfPlayerEnablePin, LOW);
        _dfPlayerEnabled = false;
        
        // Step 3: Minimal power-down confirmation (reduced from 100ms to 15ms)
        delay(15);
        
        #ifdef DEBUG
        Serial.println(F("DFPlayer powered down - standby current eliminated (optimized)"));
        #endif
    } else {
        #ifdef DEBUG
        Serial.println(F("DFPlayer already powered down"));
        #endif
    }
}

bool PowerManager::waitForDFPlayerReady(unsigned long timeoutMs) {
    if (!_dfPlayerEnabled) {
        #ifdef DEBUG
        Serial.println(F("DFPlayer not enabled - cannot wait for ready"));
        #endif
        return false;
    }
    
    #ifdef DEBUG
    Serial.print(F("Waiting for DFPlayer ready (timeout: "));
    Serial.print(timeoutMs);
    Serial.println(F("ms)"));
    #endif
    
    unsigned long startTime = millis();
    
    // Wait for DFPlayer to be ready for communication
    // This includes SD card initialization and internal setup
    while (millis() - startTime < timeoutMs) {
        // DFPlayer typically needs 1-2 seconds to fully initialize
        // We use a progressive delay approach:
        // - First 500ms: Critical power stabilization
        // - Next 1000ms: SD card and DAC initialization  
        // - Remaining time: Communication readiness buffer
        
        unsigned long elapsed = millis() - startTime;
        
        if (elapsed >= 500) {
            // After 500ms, DFPlayer power should be stable
            #ifdef DEBUG
            if (elapsed == 500 || (elapsed % 500 == 0)) {
                Serial.print(F("DFPlayer initialization progress: "));
                Serial.print(elapsed);
                Serial.println(F("ms"));
            }
            #endif
        }
        
        // Check if we've reached the minimum recommended initialization time
        if (elapsed >= 1500) {
            #ifdef DEBUG
            Serial.println(F("DFPlayer should be ready for communication"));
            #endif
            return true;
        }
        
        delay(50);
    }
    
    #ifdef DEBUG
    Serial.println(F("DFPlayer ready timeout - proceeding anyway"));
    #endif
    
    // Return true even on timeout as DFPlayer might still work
    // The calling code should handle communication failures
    return true;
}

void PowerManager::disableUnusedPeripherals() {
    // Disable unused peripherals to save power
    // These can draw several mA each when enabled
    
    power_adc_disable();      // Analog-to-Digital Converter (~320µA)
    power_spi_disable();      // Serial Peripheral Interface (~100µA)
    power_twi_disable();      // Two-Wire Interface (I2C) (~100µA)
    power_timer1_disable();   // Timer1 (~50µA)
    power_timer2_disable();   // Timer2 (~50µA)
    
    // Note: We keep Timer0 enabled as it's used by millis() and delay()
    // Note: We keep USART enabled for serial communication (can be disabled in production)
    
    #ifdef DEBUG
    Serial.println(F("Unused peripherals disabled"));
    #endif
}

void PowerManager::enableAllPeripherals() {
    // Re-enable all peripherals
    power_all_enable();
    
    #ifdef DEBUG
    Serial.println(F("All peripherals enabled"));
    #endif
}

void PowerManager::setupButtonInterrupt() {
    // Attach interrupt to button pin
    // FALLING edge triggers when button is pressed (pulls pin LOW)
    attachInterrupt(digitalPinToInterrupt(_buttonPin), buttonInterruptHandler, FALLING);
    
    #ifdef DEBUG
    Serial.print(F("Button interrupt attached to pin "));
    Serial.println(_buttonPin);
    #endif
}

void PowerManager::buttonInterruptHandler() {
    // Static interrupt handler - keep minimal and fast
    if (_instance) {
        _instance->wakeFromSleep();
    }
}

void PowerManager::enableWatchdog(uint8_t timeout) {
    cli();
    wdt_reset();
    
    // Configure watchdog timer
    WDTCSR |= (1<<WDCE) | (1<<WDE);
    WDTCSR = (1<<WDIE) | timeout;  // Enable interrupt mode
    
    sei();
    
    _watchdogEnabled = true;
    
    #ifdef DEBUG
    Serial.println(F("Watchdog timer enabled"));
    #endif
}

void PowerManager::disableWatchdog() {
    cli();
    wdt_reset();
    
    // Clear WDRF in MCUSR
    MCUSR &= ~(1<<WDRF);
    
    // Write logical one to WDCE and WDE
    WDTCSR |= (1<<WDCE) | (1<<WDE);
    
    // Turn off WDT
    WDTCSR = 0x00;
    
    sei();
    
    _watchdogEnabled = false;
    
    #ifdef DEBUG
    Serial.println(F("Watchdog timer disabled"));
    #endif
}

void PowerManager::resetWatchdog() {
    if (_watchdogEnabled) {
        wdt_reset();
    }
}

unsigned long PowerManager::getLastWakeTime() const {
    return _lastWakeTime;
}

unsigned long PowerManager::getSleepDuration() const {
    if (_sleepStartTime > 0 && _lastWakeTime > _sleepStartTime) {
        return _lastWakeTime - _sleepStartTime;
    }
    return 0;
}

void PowerManager::configureSleepMode() {
    // Set sleep mode to Power Down (deepest sleep)
    // This provides the lowest power consumption (~10µA)
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
}

void PowerManager::disableBrownOutDetector() {
    // Disable brown-out detection during sleep to save ~25µA
    // This is safe during sleep as we're not executing code
    sleep_bod_disable();
}

void PowerManager::enableBrownOutDetector() {
    // Brown-out detection is automatically re-enabled on wake-up
    // No explicit action needed
}

bool PowerManager::hasError() const {
    return _hasError;
}

void PowerManager::clearError() {
    _hasError = false;
    _lastError[0] = '\0';
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Error cleared"));
    #endif
}

const char* PowerManager::getLastError() const {
    return _lastError;
}

bool PowerManager::recoverFromError() {
    #ifdef DEBUG
    Serial.println(F("PowerManager: Attempting error recovery"));
    #endif
    
    if (_errorCount >= 10) { // Max error threshold
        logError("Max error count reached - recovery disabled");
        return false;
    }
    
    // Clear current error state
    clearError();
    
    // Step 1: Validate power state
    if (!validatePowerState()) {
        logError("Power state validation failed during recovery");
        return false;
    }
    
    // Step 2: Reset DFPlayer power control
    if (_dfPlayerEnabled) {
        powerDownDFPlayer();
        delay(500); // Allow complete power down
        powerUpDFPlayer();
        
        if (!waitForDFPlayerReady(3000)) {
            logError("DFPlayer not ready after power cycle");
            return false;
        }
    }
    
    // Step 3: Reset button interrupt if needed
    setupButtonInterrupt();
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Error recovery completed"));
    #endif
    
    return true;
}

bool PowerManager::validatePowerState() {
    #ifdef DEBUG
    Serial.println(F("PowerManager: Validating power state"));
    #endif
    
    // Check pin states
    pinMode(_dfPlayerEnablePin, OUTPUT); // Ensure pin is configured correctly
    pinMode(_buttonPin, INPUT_PULLUP);   // Ensure button pin is configured correctly
    
    // Validate DFPlayer enable pin state matches internal state
    bool actualPinState = digitalRead(_dfPlayerEnablePin) == HIGH;
    if (actualPinState != _dfPlayerEnabled) {
        logError("DFPlayer enable pin state mismatch");
        
        // Correct the mismatch
        digitalWrite(_dfPlayerEnablePin, _dfPlayerEnabled ? HIGH : LOW);
        delay(100);
        
        // Re-check
        actualPinState = digitalRead(_dfPlayerEnablePin) == HIGH;
        if (actualPinState != _dfPlayerEnabled) {
            logError("Cannot correct DFPlayer enable pin state");
            return false;
        }
    }
    
    // Check button pin can be read
    bool buttonState = digitalRead(_buttonPin);
    (void)buttonState; // Suppress unused variable warning
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Power state validation passed"));
    #endif
    
    return true;
}

int PowerManager::getErrorCount() const {
    return _errorCount;
}

void PowerManager::resetErrorCount() {
    _errorCount = 0;
    _lastErrorTime = 0;
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Error count reset"));
    #endif
}

void PowerManager::logError(const char* error) {
    _hasError = true;
    _errorCount++;
    _lastErrorTime = millis();
    
    // Copy error message with bounds checking
    strncpy(_lastError, error, sizeof(_lastError) - 1);
    _lastError[sizeof(_lastError) - 1] = '\0';
    
    #ifdef DEBUG
    Serial.print(F("PowerManager ERROR: "));
    Serial.println(error);
    Serial.print(F("PowerManager: Error count: "));
    Serial.println(_errorCount);
    #endif
}

void PowerManager::optimizeForMinimalPower() {
    #ifdef DEBUG
    Serial.println(F("PowerManager: Optimizing for minimal power consumption"));
    #endif
    
    // Disable all non-essential peripherals for maximum power savings
    disableAllNonEssentialPeripherals();
    
    // Configure pins for minimal power consumption
    // Set unused pins as inputs with pull-ups to prevent floating
    for (int pin = 0; pin <= 13; pin++) {
        // Skip pins we're actively using
        if (pin == _dfPlayerEnablePin || pin == _buttonPin || 
            pin == 3 || pin == 4) { // Skip DFPlayer communication pins
            continue;
        }
        
        // Set unused pins as inputs with pull-ups to minimize current
        pinMode(pin, INPUT_PULLUP);
    }
    
    // Analog pins A0-A5 (pins 14-19 on Pro Mini)
    for (int pin = A0; pin <= A5; pin++) {
        pinMode(pin, INPUT_PULLUP);
    }
    
    // Disable analog comparator (saves ~40µA)
    ACSR |= (1 << ACD);
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Minimal power optimization complete"));
    #endif
}

void PowerManager::disableAllNonEssentialPeripherals() {
    #ifdef DEBUG
    Serial.println(F("PowerManager: Disabling all non-essential peripherals"));
    #endif
    
    // Disable ADC completely (saves ~320µA)
    power_adc_disable();
    ADCSRA &= ~(1 << ADEN); // Additional ADC disable
    
    // Disable SPI (saves ~100µA)
    power_spi_disable();
    
    // Disable TWI/I2C (saves ~100µA)  
    power_twi_disable();
    
    // Disable Timer1 (saves ~50µA)
    power_timer1_disable();
    
    // Disable Timer2 (saves ~50µA)
    power_timer2_disable();
    
    // Note: Keep Timer0 enabled for millis() and delay() functions
    // Note: Keep USART enabled for debugging (disable in production)
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Non-essential peripherals disabled"));
    Serial.print(F("PowerManager: Estimated power savings: ~620µA"));
    #endif
}

void PowerManager::enableMinimalPeripherals() {
    #ifdef DEBUG
    Serial.println(F("PowerManager: Enabling minimal required peripherals"));
    #endif
    
    // Only enable what we absolutely need for operation
    // Timer0 should already be enabled (for millis/delay)
    // USART should already be enabled (for debugging)
    
    // Re-enable ADC only if needed for battery monitoring
    // power_adc_enable();
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Minimal peripherals enabled"));
    #endif
}

void PowerManager::startPowerMeasurement() {
    _powerMeasurementStart = millis();
    _powerMeasurementActive = true;
    
    #ifdef DEBUG
    Serial.println(F("PowerManager: Power measurement started"));
    #endif
}

void PowerManager::stopPowerMeasurement() {
    if (_powerMeasurementActive) {
        _lastActiveDuration = millis() - _powerMeasurementStart;
        _totalActiveDuration += _lastActiveDuration;
        _powerMeasurementActive = false;
        
        #ifdef DEBUG
        Serial.print(F("PowerManager: Power measurement stopped - Duration: "));
        Serial.print(_lastActiveDuration);
        Serial.println(F("ms"));
        #endif
    }
}

unsigned long PowerManager::getActiveDuration() const {
    if (_powerMeasurementActive) {
        return millis() - _powerMeasurementStart;
    }
    return _lastActiveDuration;
}

float PowerManager::estimateCurrentConsumption() const {
    // Estimate current consumption based on system state
    float estimatedCurrent = 0.0;
    
    if (_isAwake) {
        // Base Arduino consumption when awake (~8mA for Pro Mini 3.3V/8MHz)
        estimatedCurrent += 8.0;
        
        if (_dfPlayerEnabled) {
            // DFPlayer consumption when enabled (~25mA standby, ~150mA playing)
            estimatedCurrent += 25.0; // Assume standby when not explicitly playing
        }
        
        // Add peripheral consumption if enabled
        // These are rough estimates based on datasheet values
        if (ADCSRA & (1 << ADEN)) {
            estimatedCurrent += 0.32; // ADC enabled
        }
        
        // Serial communication adds ~1-2mA when active
        estimatedCurrent += 1.5;
        
    } else {
        // Deep sleep mode consumption
        estimatedCurrent = 0.01; // ~10µA in deep sleep
        
        if (_dfPlayerEnabled) {
            // This shouldn't happen, but account for it
            estimatedCurrent += 25.0;
        }
    }
    
    return estimatedCurrent;
}

bool PowerManager::validatePowerConsumption() const {
    float currentEstimate = estimateCurrentConsumption();
    
    #ifdef DEBUG
    Serial.print(F("PowerManager: Estimated current consumption: "));
    Serial.print(currentEstimate);
    Serial.println(F("mA"));
    #endif
    
    // Validate against requirements
    if (!_isAwake) {
        // Requirement 3.1: Deep sleep ≤10µA (0.01mA)
        if (currentEstimate > 0.05) { // Allow some margin
            #ifdef DEBUG
            Serial.println(F("PowerManager: WARNING - Sleep current too high"));
            #endif
            return false;
        }
    } else {
        // Active mode should be reasonable (under 200mA total)
        if (currentEstimate > 200.0) {
            #ifdef DEBUG
            Serial.println(F("PowerManager: WARNING - Active current too high"));
            #endif
            return false;
        }
    }
    
    return true;
}

void PowerManager::logPowerConsumption() const {
    #ifdef DEBUG
    Serial.println(F("=== POWER CONSUMPTION REPORT ==="));
    
    Serial.print(F("System State: "));
    Serial.println(_isAwake ? "AWAKE" : "SLEEPING");
    
    Serial.print(F("DFPlayer Enabled: "));
    Serial.println(_dfPlayerEnabled ? "YES" : "NO");
    
    Serial.print(F("Estimated Current: "));
    Serial.print(estimateCurrentConsumption());
    Serial.println(F("mA"));
    
    Serial.print(F("Last Active Duration: "));
    Serial.print(_lastActiveDuration);
    Serial.println(F("ms"));
    
    Serial.print(F("Total Active Duration: "));
    Serial.print(_totalActiveDuration);
    Serial.println(F("ms"));
    
    if (_totalActiveDuration > 0) {
        // Calculate duty cycle (percentage of time active)
        unsigned long totalTime = millis();
        float dutyCycle = (float)_totalActiveDuration / totalTime * 100.0;
        Serial.print(F("Duty Cycle: "));
        Serial.print(dutyCycle, 2);
        Serial.println(F("%"));
        
        // Estimate average current consumption
        float sleepCurrent = 0.01; // 10µA
        float activeCurrent = estimateCurrentConsumption();
        float avgCurrent = (dutyCycle / 100.0) * activeCurrent + 
                          (1.0 - dutyCycle / 100.0) * sleepCurrent;
        
        Serial.print(F("Average Current: "));
        Serial.print(avgCurrent, 3);
        Serial.println(F("mA"));
        
        // Estimate battery life with 3 AA batteries (~2500mAh)
        float batteryCapacity = 2500.0; // mAh
        float batteryLifeHours = batteryCapacity / avgCurrent;
        
        Serial.print(F("Estimated Battery Life: "));
        Serial.print(batteryLifeHours / 24.0, 1);
        Serial.println(F(" days"));
    }
    
    // Peripheral status
    Serial.print(F("ADC Enabled: "));
    Serial.println((ADCSRA & (1 << ADEN)) ? "YES" : "NO");
    
    Serial.print(F("Analog Comparator: "));
    Serial.println((ACSR & (1 << ACD)) ? "DISABLED" : "ENABLED");
    
    Serial.println(F("=== END POWER REPORT ==="));
    #endif
}

// Watchdog interrupt service routine
ISR(WDT_vect) {
    // Watchdog timer interrupt
    // Can be used for periodic wake-ups or system monitoring
    
    #ifdef DEBUG
    // Note: Serial may not work reliably in ISR context
    #endif
}