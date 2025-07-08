# Audio File Preparation Guide

This guide explains how to obtain, format, and prepare the "Ah! My groin!" audio clip for use with the DFPlayer Mini module.

## Audio Requirements

### File Specifications
- **Filenames**: `0001.wav`, `0002.wav`, `0003.wav`, etc. (up to 10 files by default)
- **Location**: `/mp3` folder on the SD card root
- **Format**: WAV (preferred) or MP3
- **Sample Rate**: 16kHz or 22kHz (recommended for clarity vs. file size)
- **Bit Depth**: 16-bit (WAV) or 128kbps+ (MP3)
- **Channels**: Mono (saves space, sufficient for speech)
- **Duration**: 2-4 seconds typical per file
- **File Size**: <1MB per file (plenty of room on any SD card)
- **Random Selection**: Device randomly selects from available files

### Why These Specifications?
- **DFPlayer Mini Compatibility**: Optimized for this specific hardware
- **Battery Life**: Lower sample rates = faster playback = longer battery life
- **Audio Quality**: 16kHz is sufficient for clear speech reproduction
- **File Size**: Smaller files load and play faster

## Step-by-Step Audio Preparation

### Step 1: Obtain the Source Audio

**Option A: Extract from Simpsons Episodes**
1. Find episodes containing various Hans Moleman scenes
2. The famous "football to the groin" scene is essential
3. Look for other Moleman moments like "I was saying Boo-urns"
4. Extract audio using video editing software

**Option B: Find Existing Audio Clips**
1. Search for "Simpsons Hans Moleman" audio clips online
2. Look for clean, high-quality versions
3. Collect multiple different Moleman quotes/sounds
4. Ensure clips contain just the desired exclamations

**Option C: Use Sound Board Apps**
1. Many Simpsons sound board apps contain multiple Moleman clips
2. Use screen recording or audio routing software to capture
3. Extract individual audio clips from recordings
4. Look for apps with good quality audio

**Recommended Sound Collection:**
- "Ah! My groin!" (original football scene)
- "I was saying Boo-urns" (movie theater scene)
- "My name is Hans" (various episodes)
- Other Moleman exclamations and reactions
- Mix of different emotional tones for variety

### Step 2: Edit the Audio Clips

**Recommended Software**:
- **Free**: Audacity (cross-platform)
- **Paid**: Adobe Audition, Logic Pro, Pro Tools
- **Online**: Online audio editors like TwistedWave

**Editing Steps for Each Clip**:

1. **Import the Audio**
   - Open your audio editing software
   - Import each source audio file
   - Load each audio into a separate project or track

2. **Identify Target Clips**
   - Find the exact moments for each Moleman quote
   - Each clip should be very short (1-4 seconds)
   - Include a small amount of silence before and after
   - Mark or label each clip for easy identification

3. **Trim Each Audio Clip**
   - Select just the desired portion for each sound
   - Include about 0.1-0.2 seconds of silence before the sound
   - Include about 0.5 seconds of silence after
   - Delete everything else for each clip

4. **Optimize Audio Levels**
   - Use the normalize function to maximize volume without clipping
   - Target: -3dB to -6dB peak levels
   - Ensure consistent volume throughout

5. **Remove Background Noise** (if present)
   - Use noise reduction tools if there's background music/sound
   - Be careful not to over-process and damage the voice quality
   - The goal is clear, punchy audio

6. **Add Fade In/Out** (optional)
   - Very short fade in (0.05 seconds) at the beginning
   - Short fade out (0.2 seconds) at the end
   - This prevents audio pops/clicks

### Step 3: Export the Audio

**For WAV Format** (Recommended):
```
File Format: WAV (Microsoft)
Sample Rate: 16000 Hz (16kHz)
Bit Depth: 16-bit
Channels: Mono
```

**For MP3 Format** (Alternative):
```
File Format: MP3
Sample Rate: 22050 Hz (22kHz)
Bit Rate: 128 kbps or higher
Channels: Mono
Quality: High/Best
```

**Export Settings in Audacity**:
1. File → Export → Export as WAV (or MP3)
2. Set sample rate to 16000 Hz
3. Set channels to Mono
4. Set bit depth to 16-bit (for WAV)
5. Click "Save"

### Step 4: Prepare the SD Card

**SD Card Requirements**:
- **Size**: Any size (even 128MB is plenty)
- **Type**: MicroSD (Class 4 or higher)
- **Format**: FAT32 (most important!)
- **Speed**: Class 4+ recommended

**Formatting Steps**:

1. **Format the SD Card**:
   - Insert SD card into computer
   - Format as FAT32 (not exFAT or NTFS!)
   - Use default cluster size
   - Quick format is fine

2. **Create Folder Structure**:
   ```
   SD Card Root/
   └── mp3/
       ├── 0001.wav  (Ah! My groin!)
       ├── 0002.wav  (I was saying Boo-urns)
       ├── 0003.wav  (My name is Hans)
       ├── 0004.wav  (Another Moleman quote)
       └── 0005.wav  (etc., up to 0010.wav by default)
   ```

3. **File Naming Rules**:
   - Folder MUST be named exactly "mp3" (lowercase)
   - Files MUST be named exactly "0001.wav", "0002.wav", etc.
   - No spaces, special characters, or capital letters
   - The DFPlayer is very picky about naming!
   - Sequential numbering starting from 0001

**Critical Naming Requirements**:
- Folder: `/mp3` (not /MP3, /music, /sounds, etc.)
- Files: `0001.wav`, `0002.wav`, `0003.wav`, etc.
- Numbers must be 4 digits with leading zeros
- Must be sequential (no gaps in numbering)

### Step 5: Test the Audio File

**Before Installing in Device**:

1. **Computer Playback Test**:
   - Play the file on your computer
   - Verify audio quality and volume
   - Check that timing is appropriate (not too long/short)

2. **DFPlayer Test** (if possible):
   - Connect DFPlayer to computer with USB-to-serial adapter
   - Test playback before final assembly
   - Verify the file plays correctly

**Quality Checklist**:
- [ ] Audio is clear and understandable
- [ ] Volume is appropriate (loud but not distorted)
- [ ] No background noise or artifacts
- [ ] Timing feels natural (not cut off abruptly)
- [ ] File plays immediately when triggered
- [ ] No silence at the beginning that causes delay

### Step 6: Advanced Audio Processing

**Optional Enhancements**:

1. **Compression/EQ**:
   - Light compression to make voice more punchy
   - EQ boost around 2-4kHz for voice clarity
   - Don't over-process - keep it natural

2. **Stereo to Mono Conversion**:
   - If source is stereo, convert to mono properly
   - Don't just delete one channel - mix them down

3. **Volume Matching**:
   - Test with actual speaker at normal listening distance
   - Adjust levels based on real-world testing

**Processing Chain Example** (in Audacity):
1. Noise Reduction (if needed)
2. Normalize to -6dB
3. Light Compressor (2:1 ratio, gentle)
4. High-pass filter at 80Hz (remove rumble)
5. Convert to Mono
6. Final normalize to -3dB

### Troubleshooting Audio Issues

**Problem: File Won't Play**
- Check file naming exactly (case sensitive!)
- Verify SD card is FAT32 formatted
- Ensure file is in `/mp3` folder
- Try re-copying file to SD card

**Problem: Poor Audio Quality**
- Check original source quality
- Verify export settings (16kHz, 16-bit, mono)
- Avoid over-compression during editing
- Test with known good audio file first

**Problem: Audio Cuts Off**
- Increase timeout in Arduino code
- Check file isn't corrupted
- Verify sufficient power to DFPlayer during playback

**Problem: Delay Before Playback**
- Remove silence from beginning of file
- Use WAV instead of MP3 (faster loading)
- Ensure SD card is fast enough (Class 4+)

**Problem: Volume Too Low/High**
- Adjust volume in Arduino code first
- If still issues, re-edit audio file levels
- Check speaker impedance (must be 8Ω)

### Configuring Arduino for Multiple Files

**Arduino Code Configuration**:
```cpp
// In ah_my_groin_device.ino, modify these constants:
const int NUM_AUDIO_FILES = 5;     // Change to match your number of files
const int MIN_TRACK_NUMBER = 1;    // First track (0001.wav)
const int MAX_TRACK_NUMBER = 5;    // Last track (0005.wav)
```

**File Naming Convention**:
```
/mp3/0001.wav  (Ah! My groin!)
/mp3/0002.wav  (I was saying Boo-urns)
/mp3/0003.wav  (My name is Hans)
/mp3/0004.wav  (Another Moleman quote)
/mp3/0005.wav  (Fifth sound effect)
etc.
```

**Random Selection Features**:
- Device automatically selects random file each time
- Avoids playing the same file twice in a row
- Works with any number of files from 1 to 255
- Simply add more files and update the constants

### Audio File Specifications Summary

| Parameter | Recommended | Alternative | Why |
|-----------|-------------|-------------|-----|
| Format | WAV | MP3 | Faster loading, better compatibility |
| Sample Rate | 16kHz | 22kHz | Good quality vs. file size balance |
| Bit Depth | 16-bit | N/A (MP3) | Standard for good quality |
| Channels | Mono | Stereo | Saves space, sufficient for speech |
| Filename | 0001.wav | 0001.mp3 | DFPlayer requirement |
| Location | /mp3/ | N/A | DFPlayer requirement |
| Duration | 2-4 sec | 1-10 sec | Optimal for this application |

### Final Notes

- Always keep backups of your edited audio files
- Test thoroughly before final assembly with multiple files
- Consider creating multiple versions with different processing for A/B testing
- The DFPlayer Mini is very particular about file formats and naming - follow the rules exactly!
- Start with 3-5 audio files for best variety without overwhelming the selection
- You can always add more files later by updating the Arduino constants

With proper audio preparation, your "Ah! My groin!" device will deliver clear, punchy audio with delightful variety that perfectly captures the comedic timing of Hans Moleman's many memorable moments! 