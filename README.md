
# PDF → Speech → Cloned Voice (Chunks) — Submission Package

This package contains:
- `app.py`: a Streamlit app to **preview**, **compare**, and **merge** sentence-level audio chunks (Base TTS vs. Cloned Voice).
- `Text.pdf`: your original input PDF.
- `audio_chunks/`: base TTS chunks (MP3).
- `clonedVoice chunks/`: cloned-voice chunks (WAV).
- `requirements.txt`: minimal dependencies for the Streamlit app.

## 1) Quickstart (Local)

1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   **Note:** `pydub` requires **ffmpeg** on your system for merging audio.  
   - Windows: Install ffmpeg via `choco install ffmpeg` (Chocolatey) or download from ffmpeg.org and add to PATH.  
   - macOS: `brew install ffmpeg`  
   - Linux: `sudo apt-get install ffmpeg`

3. Launch the app:
   ```bash
   streamlit run app.py
   ```
   Streamlit will open in your browser (default: http://localhost:8501).

## 2) Using the App

- The sidebar lets you select:
  - Source **PDF path** (defaults to `Text.pdf`) or upload a new PDF.
  - Folders for **Base TTS chunks** and **Cloned Voice chunks**.
  - Which set to **merge**, output filename, and whether to export **captions (SRT)**.
- The main area shows:
  - PDF **sentences** extracted (best-effort via PyPDF2).
  - Two tabs to preview **Cloned Voice** and **Base TTS** chunks.
  - A **Merge** section to combine the chosen set into one file and download it.

## 3) (Optional) Hook in Your Pipeline

If you want the Streamlit app to run your own generation scripts (PDF → TTS → Cloned Voice),
you can extend `app.py` to call them via `subprocess.run([...])`. Keep model paths and configs outside the repo
and expose them via environment variables or a simple config file so the app remains portable.

## 4) What to Submit

- The full project folder (including `app.py`, `Text.pdf`, and both chunk folders).
- A recording or screenshots of the app in action.
- The Medium blog and LinkedIn post included below (provided as files in this package).

## 5) Troubleshooting

- **No audio preview**: Confirm files exist in the selected folders and the extensions are supported.
- **Merge fails**: Ensure `ffmpeg` is installed and in PATH (required by `pydub`).
- **Sentences misaligned**: Filenames should contain a sentence number (e.g., `sentence_12.mp3`).
  The app pairs those numbers with extracted PDF sentences when building captions.

