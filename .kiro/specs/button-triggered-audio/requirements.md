# Requirements Document

## Introduction

This feature enhances the existing "Ah! My Groin!" sound effect device to only play audio when a big button is pressed, rather than playing continuously. The system will also be updated to use a 3 AA battery power supply (4.5V) instead of the current 2 AA battery setup (3V), providing better power delivery to the DFPlayer Mini module.

## Requirements

### Requirement 1

**User Story:** As a user, I want the audio to only play when I press the big button, so that I have control over when the sound effect is triggered.

#### Acceptance Criteria

1. WHEN the device is powered on THEN the system SHALL remain silent until the button is pressed
2. WHEN the big button is pressed THEN the system SHALL play the audio file once
3. WHEN the audio finishes playing THEN the system SHALL return to silent state
4. WHEN the button is pressed while audio is already playing THEN the system SHALL restart the audio from the beginning

### Requirement 2

**User Story:** As a user, I want the device to have reliable power delivery, so that the DFPlayer Mini operates consistently without voltage drops.

#### Acceptance Criteria

1. WHEN using 3 AA batteries THEN the system SHALL provide 4.5V to power both Arduino and DFPlayer
2. WHEN the DFPlayer is powered THEN it SHALL receive adequate voltage (4.5V) for reliable operation
3. WHEN the Arduino Pro Mini receives 4.5V on RAW pin THEN its voltage regulator SHALL provide stable 3.3V operation
4. WHEN batteries are connected in parallel to DFPlayer THEN both devices SHALL share the 4.5V supply

### Requirement 3

**User Story:** As a user, I want the device to be extremely power efficient, so that the 3 AA batteries last for months of occasional use.

#### Acceptance Criteria

1. WHEN no button is pressed THEN the system SHALL enter deep sleep mode with current consumption ≤10µA
2. WHEN in sleep mode THEN the DFPlayer SHALL be powered down completely to eliminate standby current
3. WHEN the button is pressed THEN the system SHALL wake from sleep mode within 100ms
4. WHEN audio playback completes THEN the system SHALL automatically power down DFPlayer and return to sleep mode
5. WHEN the Arduino is sleeping THEN it SHALL disable all unnecessary peripherals and use the lowest power sleep mode
6. WHEN the DFPlayer is not needed THEN its power SHALL be controlled via enable pin to eliminate standby consumption

### Requirement 4

**User Story:** As a developer, I want the button input to be properly debounced and reliable, so that single button presses don't trigger multiple audio plays.

#### Acceptance Criteria

1. WHEN the button is pressed THEN the system SHALL debounce the input to prevent multiple triggers
2. WHEN button bouncing occurs THEN only one audio playback SHALL be initiated
3. WHEN the button is held down THEN the audio SHALL play once and not repeat until button is released and pressed again
4. WHEN the button is connected to Pin 2 THEN it SHALL use interrupt-driven input for reliable detection

### Requirement 5

**User Story:** As a user, I want the power system to be simple to assemble, so that I can easily connect the 3 AA battery pack.

#### Acceptance Criteria

1. WHEN connecting the battery pack THEN the positive terminal SHALL connect to Arduino RAW pin
2. WHEN connecting the battery pack THEN the negative terminal SHALL connect to Arduino GND pin
3. WHEN DFPlayer needs power THEN it SHALL be connected in parallel to the same 4.5V supply
4. WHEN soldering connections THEN the wiring SHALL be clearly documented for assembly