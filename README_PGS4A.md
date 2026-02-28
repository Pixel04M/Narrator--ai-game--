# PGS4A Setup for Virtual Pet Game

This document describes how to set up and build the game using Pygame Subset for Android (PGS4A).

## Project Structure

```
.
├── main.py              # Main entry point with PGS4A detection
├── game.py              # Game logic with Android touch support
├── AndroidManifest.xml  # Android manifest for PGS4A
├── build.py             # Build script for PGS4A
├── requirements.txt     # Python dependencies
├── android/             # Android module stubs for desktop testing
│   ├── __init__.py
│   ├── touch.py
│   ├── keyboard.py
│   └── display.py
└── ...
```

## Running the Game

### Desktop Mode (Default)
```bash
python3 main.py
```

### Desktop with Android Mode Testing
```bash
python3 main.py --android
```

### Building APK with PGS4A

1. Install PGS4A:
   ```bash
   pip install pgsa
   ```

2. Initialize PGS4A (if not already done):
   ```bash
   pgs4a install android
   ```

3. Build the APK:
   ```bash
   python build.py
   ```

### Alternative: Using python-for-android (buildozer)

If PGS4A doesn't work, you can use python-for-android:

```bash
pip install buildozer
python build.py --buildozer
```

## PGS4A Detection

The game automatically detects whether it's running on:
- **Actual Android device**: Uses real PGS4A android module
- **Desktop with stub**: Uses the `android/` directory as a stub for testing

The detection is based on the `_is_stub` attribute in the android module.

## Touch Controls (PGS4A)

- **Single tap**: Select character
- **Single finger drag**: Pan camera
- **Two finger drag**: Pan camera
- **Tap on input box**: Show virtual keyboard

## Files Modified for PGS4A

1. **main.py**: Entry point with PGS4A detection logic
2. **game.py**: Android touch event handling and responsive UI
3. **android/**: Stub modules for desktop testing
4. **AndroidManifest.xml**: PGS4A launcher configuration
5. **requirements.txt**: PGS4A dependencies
6. **build.py**: Build script for creating APK
