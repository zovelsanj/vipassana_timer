# Vipassana Timer
Vipassana Timer application for managing meditation sessions with optional chantings and Metta Bhawana practice.
This is just my simple personal project for managing meditation sessions.
It allows setting meditation duration, toggling intro and end chantings, and optionally including Metta Bhawana practice.

## Flow Diagram

```text

                ┌── Intro ON ──> intro.mp3 ──┐
                │                             │
START ──────────┤                             ▼
                │                         TIMER
                │                             │
                │                             ▼
                │                    End ON? ───── Yes ──> end.mp3
                │                             │
                │                             │
                │                    Metta ON? ──────────> metta.mp3
                │
                └─────────────────────────────────────────> DONE
```

### Build Instructions
Install the required dependencies:
```bash
pip install -r requirements.txt
```

Build the application using PyInstaller:
```bash
pyinstaller --onefile --windowed --name "Vipassana Timer" --add-data "assets:assets" scripts/vipassana_timer.py
```

**BHAWATU SABBA MANGALAM** 🙏
