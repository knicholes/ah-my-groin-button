# Circuit Diagrams and Wiring Schematics

This document contains the circuit diagrams and wiring schematics for the "Ah! My Groin!" sound effect device using PlantUML format.

## Main Circuit Diagram

```plantuml
@startuml Sound_Effect_Device_Circuit
!theme aws-orange

rectangle "Power System" as power {
  component "2x AA Batteries\n(3V Total)" as batteries
  component "Power Switch\n(Optional)" as switch
}

rectangle "Control System" as control {
  component "Arduino Pro Mini\n3.3V/8MHz" as arduino {
    port "Pin 2 (INT0)" as pin2
    port "Pin 3 (TX)" as pin3
    port "Pin 4 (RX)" as pin4
    port "Pin 5 (Enable)" as pin5
    port "VCC" as vcc
    port "GND" as gnd
  }
}

rectangle "Audio System" as audio {
  component "DFPlayer Mini\nMP3 Module" as dfplayer {
    port "RX" as df_rx
    port "TX" as df_tx
    port "VCC" as df_vcc
    port "GND" as df_gnd
    port "SPK+" as spk_pos
    port "SPK-" as spk_neg
    port "Enable" as df_enable
  }
  
  component "8Ω 2W Speaker" as speaker {
    port "+" as spk_p
    port "-" as spk_n
  }
  
  component "MicroSD Card\n(Audio Files)" as sdcard
}

rectangle "Input System" as input {
  component "Big Red Button\n(Emergency Stop Style)" as button {
    port "Terminal 1" as btn1
    port "Terminal 2" as btn2
  }
}

' Power connections
batteries --> switch
switch --> vcc
batteries --> gnd
vcc --> df_vcc
gnd --> df_gnd

' Serial communication
pin3 --> df_rx : Serial Data
pin4 --> df_tx : Serial Data

' Power control (optional)
pin5 --> df_enable : Enable Control

' Button connection
pin2 --> btn1 : Button Input
btn2 --> gnd : Ground

' Speaker connection
spk_pos --> spk_p : Audio+
spk_neg --> spk_n : Audio-

' SD card
sdcard --> dfplayer : Insert into slot

note right of arduino
  Remove power LED
  for battery efficiency
end note

note right of dfplayer
  Built-in 3W amplifier
  Supports MP3/WAV files
end note

note right of button
  Momentary contact
  Normally open
  3-4" diameter
end note

@enduml
```

## Detailed Wiring Schematic

```plantuml
@startuml Detailed_Wiring_Schematic
!theme blueprint

' Define components with pin layouts
rectangle "Arduino Pro Mini" as arduino {
  rectangle "Digital Pins" {
    (Pin 2) as d2
    (Pin 3) as d3
    (Pin 4) as d4
    (Pin 5) as d5
  }
  rectangle "Power Pins" {
    (VCC) as vcc
    (GND) as gnd
  }
}

rectangle "DFPlayer Mini" as dfplayer {
  rectangle "Communication" {
    (RX) as df_rx
    (TX) as df_tx
  }
  rectangle "Power" {
    (VCC) as df_vcc
    (GND) as df_gnd
  }
  rectangle "Audio Output" {
    (SPK+) as spk_pos
    (SPK-) as spk_neg
  }
  rectangle "Control" {
    (Enable) as df_enable
  }
}

rectangle "Power Supply" as power {
  (Battery +) as bat_pos
  (Battery -) as bat_neg
  (Switch) as sw
}

rectangle "External Components" {
  (Button Terminal 1) as btn1
  (Button Terminal 2) as btn2
  (Speaker +) as spk_p
  (Speaker -) as spk_n
}

' Wire connections with labels
bat_pos --> sw : Red Wire
sw --> vcc : Red Wire (3V)
bat_neg --> gnd : Black Wire
vcc --> df_vcc : Red Wire (3V)
gnd --> df_gnd : Black Wire

d3 --> df_rx : Yellow Wire (Arduino TX)
d4 --> df_tx : Green Wire (Arduino RX)
d5 --> df_enable : Blue Wire (Optional)

d2 --> btn1 : Orange Wire
btn2 --> gnd : Black Wire

spk_pos --> spk_p : Red Wire
spk_neg --> spk_n : Black Wire

note top of arduino
Pull-up resistor enabled
in software for Pin 2
end note

note bottom of dfplayer
Files named 0001.wav
in /mp3 folder on SD card
end note

@enduml
```

## Power Management Diagram

```plantuml
@startuml Power_Management_Flow
!theme aws-orange

start

:Device Powered Off\n(0 µA current);

:User Presses Button;

:Arduino Wakes from Sleep\n(Pin 2 Interrupt);

:Enable DFPlayer\n(Pin 5 High);

:Send Play Command\nto DFPlayer;

:Audio Playing\n(~150mA current);

:Wait for Audio\nto Complete;

:Disable DFPlayer\n(Pin 5 Low);

:Arduino Returns\nto Sleep Mode\n(~10 µA current);

stop

note right
  Sleep mode saves significant
  battery life between uses
end note

@enduml
```

## Component Layout Diagram

```plantuml
@startuml Physical_Layout
!theme plain

rectangle "Enclosure (4\" x 3\" x 1.5\")" {
  
  rectangle "Top Panel" {
    circle "Big Red Button\n(3-4\" diameter)" as button
  }
  
  rectangle "Internal Layout" {
    rectangle "Main PCB Area" {
      component "Arduino\nPro Mini" as arduino
      component "DFPlayer\nMini" as dfplayer
    }
    
    rectangle "Audio Section" {
      component "Speaker\n(2-3\")" as speaker
      component "SD Card\nSlot" as sdcard
    }
    
    rectangle "Power Section" {
      component "Battery\nHolder" as batteries
      component "Power\nSwitch" as switch
    }
  }
  
  rectangle "Side Panel" {
    component "Volume Control\n(Optional)" as volume
    component "Charging Port\n(Optional)" as charging
  }
}

button --> arduino : Button Wires
arduino --> dfplayer : Serial + Power
dfplayer --> speaker : Audio Output
dfplayer --> sdcard : Data Lines
batteries --> arduino : Power
switch --> batteries : Power Control

note right of button
  Mounted through
  top panel for
  easy access
end note

note right of speaker
  Speaker grille
  on front or
  bottom panel
end note

@enduml
```

## Assembly Process Flow

```plantuml
@startuml Assembly_Process
!theme blueprint

start

:Gather All Components;

:Prepare Arduino Pro Mini\n(Remove power LED);

:Prepare DFPlayer Mini\n(Solder header pins);

:Create Test Circuit\non Breadboard;

:Upload and Test\nArduino Code;

:Verify Audio Playback;

if (Everything Working?) then (yes)
  :Prepare Enclosure\n(Drill holes);
  :Mount Components\nin Enclosure;
  :Connect All Wiring;
  :Final Testing;
  :Close Enclosure;
  :Quality Control Check;
  stop
else (no)
  :Troubleshoot Issues;
  :Check Connections;
  :Verify Code Upload;
  :Test Components;
endif

@enduml
```

## Power Consumption Analysis

```plantuml
@startuml Power_Analysis
!theme aws-orange

state "Power States" as power_states {
  state "Sleep Mode" as sleep {
    sleep : Current: ~10 µA
    sleep : Duration: 99% of time
    sleep : Power: ~0.03 mW
  }
  
  state "Wake Mode" as wake {
    wake : Current: ~20 mA
    wake : Duration: 1-2 seconds
    wake : Power: ~60 mW
  }
  
  state "Play Mode" as play {
    play : Current: ~150 mA
    play : Duration: 2-3 seconds
    play : Power: ~450 mW
  }
}

sleep --> wake : Button Press
wake --> play : Audio Start
play --> sleep : Audio Complete

note right of sleep
  Arduino in deep sleep
  DFPlayer powered off
  Only button interrupt active
end note

note right of play
  DFPlayer active
  Speaker driven
  Maximum current draw
end note

@enduml
```

## Troubleshooting Decision Tree

```plantuml
@startuml Troubleshooting_Tree
!theme blueprint

start

:Device Not Working;

if (Any power LED on?) then (no)
  :Check battery voltage;
  :Check power connections;
  :Replace batteries if needed;
else (yes)
  if (Button responds?) then (no)
    :Check button connections;
    :Verify button continuity;
    :Check Arduino Pin 2;
  else (yes)
    if (Audio plays?) then (no)
      :Check DFPlayer power;
      :Verify SD card format;
      :Check audio file names;
      :Test speaker connections;
    else (yes)
      if (Audio quality poor?) then (yes)
        :Check speaker impedance (8Ω);
        :Verify file format;
        :Adjust volume settings;
      else (no)
        :Device working normally;
        stop
      endif
    endif
  endif
endif

@enduml
```

These diagrams provide a comprehensive view of the system architecture, wiring requirements, and assembly process for the sound effect device. 