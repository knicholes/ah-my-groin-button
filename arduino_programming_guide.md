# Arduino Pro Mini Programming Guide

## Overview
The Arduino Pro Mini doesn't have a built-in USB connector, so you need a special programmer to upload firmware. This guide covers multiple programming methods and troubleshooting for the "Ah! My Groin!" device.

## Programming Methods

You have several options for programming the Arduino Pro Mini:

### Method 1: USB-to-Serial Adapter (⭐ Recommended)

**What You Need:**
- **USB-to-Serial adapter** (FTDI FT232RL or CP2102 based)
- **6-pin connector** or individual jumper wires
- **Arduino IDE** installed on your computer

**Recommended Adapters:**
- **SparkFun FTDI Basic Breakout 3.3V** - $16.95 (Part #DEV-09873)
- **Adafruit FTDI Friend** - $14.75 (Part #284)
- **Generic CP2102 USB-to-TTL** - $3-8 (Amazon/eBay)

**Advantages:**
- ✅ Most popular and well-supported method
- ✅ Can power the Arduino during programming
- ✅ Widely available and affordable
- ✅ Works with Arduino IDE directly

### Method 2: Arduino Uno as Programmer

**What You Need:**
- **Arduino Uno** (or any Arduino with USB)
- **Jumper wires** (male-to-male)
- **Arduino IDE**

**Advantages:**
- ✅ Use existing Arduino hardware
- ✅ No additional purchase needed
- ✅ Good for one-time programming

**Disadvantages:**
- ❌ More complex setup
- ❌ Requires removing ATmega328P chip from Uno

### Method 3: Dedicated Arduino Programmer

**What You Need:**
- **Arduino ISP programmer** (like USBasp or Arduino as ISP)
- **6-pin ISP connector**

**Advantages:**
- ✅ Most reliable method
- ✅ Works even if bootloader is corrupted

**Disadvantages:**
- ❌ More expensive
- ❌ Requires ISP programming knowledge

## DETAILED PROGRAMMING INSTRUCTIONS

### Method 1: USB-to-Serial Adapter Setup

#### Step 1: Install Arduino IDE
1. **Download Arduino IDE** from [arduino.cc](https://www.arduino.cc/en/software)
2. **Install the software** on your computer
3. **Launch Arduino IDE** and verify it opens correctly

#### Step 2: Install Device Drivers
**For FTDI-based adapters:**
1. **Windows**: Drivers usually install automatically
2. **Mac**: Download from [FTDI website](https://ftdichip.com/drivers/vcp-drivers/)
3. **Linux**: Usually built into kernel

**For CP2102-based adapters:**
1. **Windows**: Download from [Silicon Labs](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
2. **Mac**: Download from Silicon Labs website
3. **Linux**: Usually built into kernel

#### Step 3: Physical Connection
```
USB-to-Serial Adapter → Arduino Pro Mini
==================================
VCC (3.3V) → VCC
GND → GND
TX → RX-I (Pin 0)
RX → TX-O (Pin 1)
DTR → DTR (for auto-reset)
CTS → CTS (optional)

CRITICAL: Use 3.3V, NOT 5V!
```

**Visual Wiring Diagram:**
```
USB-to-Serial Adapter        Arduino Pro Mini
┌─────────────────────┐     ┌─────────────────────┐
│  GND │ CTS │ VCC    │     │ GND │ VCC │ RST │   │
│  TXD │ RXD │ DTR    │     │ RXI │ TXO │ DTR │   │
└─────────────────────┘     └─────────────────────┘
   │     │     │               │     │     │
   │     │     └───────────────┘     │     │
   │     └─────────────────────────────┘     │
   └─────────────────────────────────────────┘
```

#### Step 4: Arduino IDE Configuration
1. **Open Arduino IDE**
2. **Go to Tools → Board → Arduino AVR Boards**
3. **Select "Arduino Pro or Pro Mini"**
4. **Go to Tools → Processor**
5. **Select "ATmega328P (3.3V, 8MHz)"** ⚠️ **CRITICAL: Must be 3.3V/8MHz**
6. **Go to Tools → Port**
7. **Select the COM port** for your USB-to-Serial adapter

#### Step 5: Load the Firmware
1. **Open the firmware file** (`ah_my_groin_device.ino`)
2. **Click the Upload button** (right arrow icon)
3. **Watch the upload progress** in the status bar
4. **Wait for "Done uploading"** message

**Expected Upload Output:**
```
Sketch uses 8,234 bytes (26%) of program storage space.
Global variables use 445 bytes (21%) of dynamic memory.
Done uploading.
```

### Method 2: Arduino Uno as Programmer

#### Step 1: Prepare Arduino Uno
1. **Remove ATmega328P chip** from Arduino Uno (carefully!)
2. **Connect jumper wires** as shown below:

```
Arduino Uno → Arduino Pro Mini
===========================
5V → VCC (only if Pro Mini is 5V version)
3.3V → VCC (for 3.3V Pro Mini)
GND → GND
Pin 0 (RX) → Pin 1 (TX)
Pin 1 (TX) → Pin 0 (RX)
RST → RST
```

#### Step 2: Arduino IDE Configuration
1. **Select Arduino Uno** as the board
2. **Select correct COM port** for the Uno
3. **Upload the firmware** normally

### Method 3: ISP Programming (Advanced)

#### Step 1: Setup ISP Programmer
1. **Connect ISP programmer** to Arduino Pro Mini ISP header
2. **Connect power supply** (3.3V for Pro Mini)

#### Step 2: Arduino IDE Configuration
1. **Go to Tools → Programmer**
2. **Select your ISP programmer** (USBasp, Arduino as ISP, etc.)
3. **Go to Sketch → Upload Using Programmer**

## TROUBLESHOOTING

### Common Upload Errors

#### Error: "avrdude: stk500_recv(): programmer is not responding"
**Causes:**
- Wrong COM port selected
- Adapter not connected properly
- Driver issues
- Wrong board/processor selection

**Solutions:**
1. **Check COM port** in Device Manager (Windows)
2. **Verify physical connections** (especially DTR for auto-reset)
3. **Try different USB port**
4. **Reinstall drivers**

#### Error: "avrdude: stk500_getsync(): not in sync"
**Causes:**
- Wrong baud rate
- Bootloader corruption
- Timing issues

**Solutions:**
1. **Press reset** manually during upload
2. **Check baud rate** (should be 57600 for Pro Mini)
3. **Try uploading immediately** after connecting power

#### Error: "Board not found" or "Device not recognized"
**Causes:**
- Driver not installed
- Wrong USB-to-Serial adapter
- Hardware failure

**Solutions:**
1. **Install correct drivers**
2. **Test adapter with multimeter** (should output 3.3V)
3. **Try different adapter**

### Manual Reset Technique

If auto-reset isn't working:
1. **Click Upload** in Arduino IDE
2. **Wait for "Uploading..."** message
3. **Press and release reset button** on Arduino Pro Mini
4. **Upload should start** within 2-3 seconds

### Verifying Upload Success

#### Method 1: Serial Monitor Test
```cpp
void setup() {
  Serial.begin(9600);
  Serial.println("Ah! My Groin! Device - Firmware loaded successfully!");
}

void loop() {
  // Add this to the main code temporarily
  Serial.println("Device running...");
  delay(5000);
}
```

#### Method 2: LED Blink Test
```cpp
void setup() {
  pinMode(13, OUTPUT);  // Built-in LED (if available)
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
```

#### Method 3: Button Test
- **Connect button** to Pin 2 and GND
- **Press button** → Should see response in serial monitor
- **Verify DFPlayer communication** (if connected)

## FIRMWARE CONFIGURATION

### Before First Upload

#### Required Libraries
The firmware uses these libraries (install via Library Manager):
- **SoftwareSerial** (built-in)
- **avr/sleep.h** (built-in)
- **avr/power.h** (built-in)
- **avr/wdt.h** (built-in)

#### Configuration Options
Edit these constants in the firmware:
```cpp
// Audio file configuration
const int NUM_AUDIO_FILES = 10;     // Number of files (0001.wav to 0010.wav)
const int MIN_TRACK_NUMBER = 1;     // First track number
const int MAX_TRACK_NUMBER = 10;    // Last track number

// Volume and timing
const int DEFAULT_VOLUME = 25;      // Volume level (0-30)
const unsigned long DEBOUNCE_DELAY = 200;  // Button debounce (ms)
const unsigned long PLAY_TIMEOUT = 5000;   // Max play time (ms)
```

### Debug Mode
For troubleshooting, enable debug mode:
```cpp
#define DEBUG  // Add this line at the top of the file
```

This will enable serial output for debugging.

## PRODUCTION FIRMWARE STEPS

### Step 1: Test Upload
1. **Upload firmware** with DEBUG enabled
2. **Open Serial Monitor** (Tools → Serial Monitor)
3. **Set baud rate** to 9600
4. **Press reset** on Arduino
5. **Verify startup messages** appear

### Step 2: Test Hardware
1. **Connect DFPlayer Mini** and speaker
2. **Insert SD card** with audio files
3. **Connect button** to Pin 2
4. **Press button** → Should play audio

### Step 3: Final Programming
1. **Remove DEBUG line** from firmware
2. **Upload final firmware**
3. **Disconnect programmer**
4. **Test with batteries**

## ADVANCED PROGRAMMING OPTIONS

### Bootloader Installation
If bootloader gets corrupted:
1. **Use ISP programmer**
2. **Go to Tools → Burn Bootloader**
3. **Select Arduino Pro Mini 3.3V/8MHz**
4. **Wait for completion**

### Fuse Settings
Correct fuse settings for 3.3V/8MHz:
- **Low Fuse**: 0xE2
- **High Fuse**: 0xDA
- **Extended Fuse**: 0xFD

### Programming via ISP Header
Arduino Pro Mini ISP header pinout:
```
ISP Header (6-pin, 2x3):
┌─────┬─────┐
│ VCC │ MISO│
├─────┼─────┤
│ SCK │ MOSI│
├─────┼─────┤
│ RST │ GND │
└─────┴─────┘
```

## FREQUENTLY ASKED QUESTIONS

**Q: Can I use a 5V USB-to-Serial adapter?**
A: No! The Arduino Pro Mini 3.3V/8MHz must use 3.3V logic levels. 5V will damage the board.

**Q: Do I need to remove the Arduino from the circuit to program it?**
A: No, you can program it in-circuit, but ensure nothing interferes with the programming pins.

**Q: Can I program multiple Arduino Pro Minis with the same firmware?**
A: Yes, just repeat the upload process for each board.

**Q: What if the upload fails repeatedly?**
A: Try the manual reset technique, check all connections, and verify driver installation.

**Q: Can I modify the firmware after uploading?**
A: Yes, just make changes and upload again. The new firmware will overwrite the old one.

## PURCHASING RECOMMENDATIONS

### Budget Programming Setup (~$8-15)
- **Generic CP2102 USB-to-TTL adapter** - $3-8
- **Jumper wires** - $3-5
- **Total**: $8-15

### Professional Programming Setup (~$25-35)
- **SparkFun FTDI Basic Breakout 3.3V** - $16.95
- **6-pin programming cable** - $5-10
- **Total**: $25-35

### Complete Development Kit (~$50-75)
- **Arduino Uno** (as backup programmer) - $25
- **USB-to-Serial adapter** - $15
- **Breadboard and jumper wires** - $10
- **Total**: $50-75

## NEXT STEPS

After successfully uploading the firmware:
1. **Test basic functionality** with serial monitor
2. **Connect audio hardware** (DFPlayer, speaker, SD card)
3. **Test button response** and audio playback
4. **Proceed to final assembly** in enclosure
5. **Perform final system testing**

Remember: Always double-check your connections and use the correct voltage levels (3.3V) to avoid damaging your Arduino Pro Mini! 