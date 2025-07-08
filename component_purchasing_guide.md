# Component Purchasing Guide

This guide provides specific component recommendations, part numbers, and purchasing sources for building the "Ah! My Groin!" sound effect device.

## Complete Component List with Prices (USD)

| Component | Quantity | Est. Price | Total |
|-----------|----------|------------|-------|
| Arduino Pro Mini 3.3V/8MHz | 1 | $8-12 | $10 |
| DFPlayer Mini MP3 Module | 1 | $3-5 | $4 |
| Big Red Emergency Button | 1 | $15-25 | $20 |
| 8Ω 2W Speaker | 1 | $5-8 | $6 |
| MicroSD Card (8GB+) | 1 | $5-10 | $7 |
| 2x AA Battery Holder | 1 | $3-5 | $4 |
| Project Enclosure | 1 | $8-15 | $12 |
| Hookup Wire | 1 pack | $5-8 | $6 |
| Misc (resistors, headers) | 1 kit | $10-15 | $12 |
| **Total Estimated Cost** | | | **$81** |

*Prices may vary by supplier and shipping costs not included*

## Core Components - Detailed Specifications

### 1. Microcontroller: Arduino Pro Mini

**Recommended Specifications:**
- **Voltage**: 3.3V (CRITICAL - must match battery voltage)
- **Clock Speed**: 8MHz (lower power consumption)
- **Microcontroller**: ATmega328P
- **Size**: 18mm x 33mm
- **I/O Pins**: 14 digital, 6 analog

**Specific Product Recommendations:**

**Option A: SparkFun Arduino Pro Mini 3.3V/8MHz** ⭐ *Recommended*
- **Part Number**: DEV-11114
- **Price**: ~$10
- **Source**: SparkFun, Amazon, DigiKey
- **Pros**: High quality, reliable, good documentation
- **Cons**: Slightly more expensive

**Option B: Generic Arduino Pro Mini Clone**
- **Search Terms**: "Arduino Pro Mini 3.3V 8MHz ATmega328P"
- **Price**: ~$3-5
- **Source**: AliExpress, eBay, Amazon
- **Pros**: Very inexpensive
- **Cons**: Quality varies, longer shipping

**Purchase Links:**
- [SparkFun](https://www.sparkfun.com/products/11114)
- [Amazon Search](https://amazon.com/s?k=arduino+pro+mini+3.3v+8mhz)
- [DigiKey](https://www.digikey.com/en/products/detail/sparkfun-electronics/DEV-11114)

### 2. Audio Module: DFPlayer Mini

**Specifications:**
- **Input Voltage**: 3.2V-5V (perfect for 3V battery)
- **Output Power**: 3W (built-in amplifier)
- **Audio Formats**: MP3, WAV, WMA
- **Storage**: MicroSD up to 32GB
- **Communication**: UART/Serial
- **Size**: 20mm x 20mm

**Specific Product Recommendations:**

**Option A: Genuine DFPlayer Mini** ⭐ *Recommended*
- **Part Number**: DFR0299 (DFRobot)
- **Price**: ~$4-6
- **Source**: DFRobot, Amazon, Adafruit
- **Pros**: Reliable, good documentation, consistent quality

**Option B: Generic DFPlayer Mini Clone**
- **Search Terms**: "DFPlayer Mini MP3 Module"
- **Price**: ~$2-4
- **Source**: AliExpress, eBay, Amazon
- **Pros**: Very affordable
- **Cons**: Quality inconsistent, may need troubleshooting

**Purchase Links:**
- [DFRobot Official](https://www.dfrobot.com/product-1121.html)
- [Amazon Search](https://amazon.com/s?k=dfplayer+mini+mp3)
- [Adafruit](https://www.adafruit.com/product/3000)

### 3. Big Red Button: Emergency Stop Button

**Specifications:**
- **Type**: Momentary contact, normally open
- **Size**: 60mm-100mm diameter (3-4 inches)
- **Style**: Mushroom head emergency stop
- **Mounting**: Panel mount with nut
- **Contacts**: SPST (Single Pole, Single Throw)
- **Current Rating**: 10A+ (overkill but standard)

**Specific Product Recommendations:**

**Option A: Eaton/Moeller Emergency Stop Button** ⭐ *Recommended*
- **Part Number**: M22-PVT45P-R
- **Size**: 40mm mushroom head
- **Price**: ~$15-20
- **Source**: DigiKey, Mouser, Automation Direct
- **Pros**: High quality, satisfying click, durable

**Option B: Generic Red Emergency Stop Button**
- **Search Terms**: "60mm red emergency stop button mushroom"
- **Price**: ~$8-15
- **Source**: Amazon, eBay, electrical supply stores
- **Pros**: Much cheaper, good visual impact
- **Cons**: Build quality varies

**Option C: Arcade Button (Alternative)**
- **Part Number**: Various 60mm arcade buttons
- **Price**: ~$10-15
- **Source**: Arcade parts suppliers, Amazon
- **Pros**: Fun retro feel, various colors available
- **Cons**: Less "emergency" aesthetic

**Purchase Links:**
- [DigiKey Emergency Stops](https://www.digikey.com/en/products/filter/pushbutton-switches/199?s=N4IgjCBcpgbFoDGUBmBDANgZwKYBoQB7KAbRAGYAGABjQFYAOAFgDYBOBsgBgFcBbAHYBmALgBfLRBC60GHF0QAGWk03tOAI1Z9B4AY0hQS)
- [Amazon Search](https://amazon.com/s?k=red+emergency+stop+button+60mm)

### 4. Speaker: 8Ω 2-3W Speaker

**Specifications:**
- **Impedance**: 8Ω (CRITICAL for DFPlayer compatibility)
- **Power**: 2-3W RMS
- **Size**: 2-3 inches diameter
- **Frequency Response**: 100Hz-10kHz minimum
- **Mounting**: Screw holes or clips

**Specific Product Recommendations:**

**Option A: Visaton FR 7 Fullrange Speaker** ⭐ *Recommended*
- **Part Number**: 2114
- **Size**: 70mm (2.8")
- **Power**: 2W
- **Price**: ~$8-12
- **Source**: Parts Express, Amazon
- **Pros**: Excellent clarity for voice, compact size

**Option B: Peerless by Tymphany TC6FD Speaker**
- **Size**: 2.25"
- **Power**: 3W
- **Price**: ~$10-15
- **Source**: Parts Express, Madisound

**Option C: Generic 8Ω 3W Speaker**
- **Search Terms**: "8 ohm 3 watt speaker 57mm"
- **Price**: ~$3-6
- **Source**: Amazon, eBay, electronics stores
- **Pros**: Very affordable
- **Cons**: Quality varies significantly

**Purchase Links:**
- [Parts Express Speakers](https://www.parts-express.com/cat/full-range-speakers/286)
- [Amazon Search](https://amazon.com/s?k=8+ohm+3+watt+speaker)

### 5. Storage: MicroSD Card

**Specifications:**
- **Capacity**: 8GB minimum (huge overkill for this project)
- **Class**: Class 4 or higher
- **Format**: Must be FAT32 compatible
- **Brand**: SanDisk, Kingston, Samsung recommended

**Specific Product Recommendations:**

**Option A: SanDisk Ultra 16GB MicroSD** ⭐ *Recommended*
- **Part Number**: SDSQUAR-016G
- **Price**: ~$5-8
- **Source**: Amazon, Best Buy, Walmart
- **Pros**: Reliable brand, fast, widely available

**Option B: Any Brand 8GB+ MicroSD**
- **Requirements**: FAT32 compatible, Class 4+
- **Price**: ~$3-6
- **Source**: Anywhere
- **Note**: Even cheap cards work fine for this application

**Purchase Links:**
- [Amazon MicroSD](https://amazon.com/s?k=sandisk+microsd+16gb)

### 6. Power System: Battery Holder

**Specifications:**
- **Type**: 2x AA battery holder
- **Switch**: Built-in on/off switch preferred
- **Leads**: 6" flying leads or barrel connector
- **Mounting**: Screw holes or adhesive backing

**Specific Product Recommendations:**

**Option A: Keystone 2466 Battery Holder** ⭐ *Recommended*
- **Part Number**: 2466
- **Features**: 2x AA, on/off switch, 6" leads
- **Price**: ~$3-5
- **Source**: DigiKey, Mouser, Amazon
- **Pros**: Quality construction, built-in switch

**Option B: Generic 2x AA Holder with Switch**
- **Search Terms**: "2 AA battery holder switch wires"
- **Price**: ~$2-4
- **Source**: Amazon, eBay, electronics stores

**Purchase Links:**
- [DigiKey Battery Holders](https://www.digikey.com/en/products/filter/battery-holders-clips-contacts/84)
- [Amazon Search](https://amazon.com/s?k=2+AA+battery+holder+switch)

### 7. Enclosure: Project Box

**Specifications:**
- **Size**: ~4" x 3" x 1.5" (100mm x 75mm x 40mm)
- **Material**: ABS plastic preferred
- **Color**: Any (will be mostly hidden)
- **Features**: Screw-on lid, mounting posts helpful

**Specific Product Recommendations:**

**Option A: Hammond 1591XXFLBK Enclosure** ⭐ *Recommended*
- **Part Number**: 1591XXFLBK
- **Size**: 4.53" x 2.56" x 1.38"
- **Price**: ~$8-12
- **Source**: DigiKey, Mouser, Amazon
- **Pros**: Professional appearance, easy to modify

**Option B: Generic Project Box**
- **Search Terms**: "ABS plastic enclosure 100mm x 75mm"
- **Price**: ~$5-10
- **Source**: Amazon, eBay, electronics stores

**Purchase Links:**
- [DigiKey Enclosures](https://www.digikey.com/en/products/filter/boxes-enclosures-racks/576)
- [Amazon Search](https://amazon.com/s?k=plastic+project+box+electronics)

## Miscellaneous Components

### 8. Connecting Wire

**Required:**
- **Type**: 22-24 AWG stranded hookup wire
- **Colors**: Red, black, yellow, green, blue minimum
- **Length**: 10-20 feet total
- **Insulation**: PVC, various colors

**Recommendation:**
- **Product**: Remington Industries 22 AWG Hook Up Wire Kit
- **Price**: ~$15-20 for assorted kit
- **Source**: Amazon, electronics suppliers

### 9. Headers and Connectors

**Required:**
- Male header pins (for Arduino Pro Mini)
- Female headers (optional, for removable connections)
- Heat shrink tubing (for wire protection)

**Recommendation:**
- **Product**: Electronics prototyping kit with headers
- **Price**: ~$10-15
- **Source**: Amazon, electronics suppliers

## Complete Purchasing Strategy

### Budget Option (~$50 total)
- Generic Arduino Pro Mini clone ($3-5)
- Generic DFPlayer Mini ($2-4)
- Generic red button ($8-12)
- Generic speaker ($3-6)
- Cheap MicroSD card ($3-5)
- Basic battery holder ($2-4)
- Generic project box ($5-8)
- Wire and misc ($10-15)

### Recommended Option (~$81 total)
- SparkFun Arduino Pro Mini ($10)
- Genuine DFPlayer Mini ($4-6)
- Quality emergency stop button ($15-20)
- Visaton speaker ($8-12)
- SanDisk MicroSD card ($5-8)
- Keystone battery holder ($3-5)
- Hammond enclosure ($8-12)
- Quality wire and components ($15-20)

### Premium Option (~$120 total)
- All recommended components plus:
- Custom PCB instead of breadboard/perfboard ($20-30)
- Premium speaker with better response
- Metal enclosure with professional finish
- Higher quality switches and connectors

## Recommended Suppliers

### For Individual Components:
1. **DigiKey** - Best for professional-grade components
2. **Mouser** - Great selection, fast shipping
3. **SparkFun** - Arduino specialists, educational focus
4. **Adafruit** - Great tutorials and support
5. **Amazon** - Fast shipping, one-stop shopping
6. **eBay** - Budget options, international sellers

### For Bulk/Kits:
1. **Amazon** - Arduino starter kits with components
2. **AliExpress** - Very cheap, longer shipping times
3. **Banggood** - Good middle ground for price/quality

## Shipping and Timing Considerations

### Fast Shipping (1-3 days):
- Amazon Prime
- Local electronics stores (Micro Center, etc.)
- DigiKey/Mouser (next day available)

### Standard Shipping (1-2 weeks):
- Most US suppliers
- SparkFun, Adafruit

### Economy Shipping (2-6 weeks):
- AliExpress, eBay (from Asia)
- Only choose if budget is very tight

## Money-Saving Tips

1. **Buy Arduino kits** - Often cheaper than individual components
2. **Combine orders** - Save on shipping by ordering multiple items
3. **Check local stores** - Sometimes competitive with online prices
4. **Consider clones** - Generic Arduino/DFPlayer work fine for this project
5. **Reuse components** - Check if you have suitable enclosure, wire, etc.

## Quality vs. Price Guidance

### Splurge On:
- **Button** - This is the main interaction, get a satisfying one
- **Speaker** - Audio quality matters for the effect
- **Enclosure** - A nice box makes the whole project feel premium

### Save On:
- **Arduino** - Clones work fine for this simple application
- **MicroSD card** - Any working card is sufficient
- **Wire** - Basic hookup wire is perfectly adequate

### Test First:
- **DFPlayer Mini** - Quality varies with clones, test thoroughly

## Alternative Sources

### Local Options:
- **Electronics stores** (Fry's, Micro Center, RadioShack if still open)
- **Industrial suppliers** (Grainger, McMaster-Carr for buttons)
- **Surplus stores** - Sometimes have great deals on components

### International Options:
- **AliExpress** - Huge selection, very cheap, slow shipping
- **Banggood** - Good compromise between price and speed
- **LCSC** - Growing supplier with good prices

This purchasing guide should give you everything needed to source components efficiently and cost-effectively for your "Ah! My Groin!" sound effect device! 