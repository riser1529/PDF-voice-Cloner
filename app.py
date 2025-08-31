
import streamlit as st
from pathlib import Path
import re
from io import BytesIO

# Optional dependencies
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None

st.set_page_config(page_title="PDF → Speech → Cloned Voice (Chunks)", layout="wide")

st.title("📄→🔊 PDF to Speech (with Cloned Voice) — Chunk Reviewer")

st.markdown(
    "This app lets you **preview sentence-level audio chunks** generated from a PDF, "
    "compare base TTS vs. cloned-voice outputs, and **merge** them into a single file with optional captions."
)

# Project defaults (detected from your uploaded project)
default_pdf = Path("Text.pdf")
base_chunks_dir = Path("audio_chunks")
cloned_chunks_dir = Path("clonedVoice chunks")

with st.sidebar:
    st.header("Project Inputs")
    pdf_path = st.text_input("PDF path", value=str(default_pdf), help="Path to the source PDF used to generate the audio.")
    st.caption("Upload a different PDF if you like:")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        # Save uploaded to a temp path
        tmp_pdf = Path("uploaded.pdf")
        tmp_pdf.write_bytes(uploaded_pdf.read())
        pdf_path = str(tmp_pdf)

    st.divider()
    st.subheader("Chunk Folders")
    base_dir = st.text_input("Base TTS chunks (mp3)", value=str(base_chunks_dir))
    clone_dir = st.text_input("Cloned voice chunks (wav)", value=str(cloned_chunks_dir))

    st.divider()
    st.subheader("Merge Options")
    target_choice = st.selectbox("Which set to merge?", ["Cloned voice", "Base TTS"])
    output_name = st.text_input("Output filename", value="merged_output.wav")

    make_srt = st.checkbox("Also create captions (SRT)", value=True)

def read_pdf_sentences(path: str):
    sentences = []
    p = Path(path)
    if not p.exists():
        return sentences
    if PdfReader is None:
        return sentences
    try:
        reader = PdfReader(str(p))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        # Naive sentence split: split by . ! ? while keeping them
        import re
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [s.strip() for s in parts if s.strip()]
    except Exception as e:
        st.warning(f"Failed to parse PDF: {e}")
    return sentences

# Extract numeric index from filenames like 'sentence_12.mp3' or 'Sentence 12.wav'
def extract_index(name: str):
    m = re.search(r"(?:sentence|Sentence)[ _-]?(\d+)", name)
    return int(m.group(1)) if m else 10**9  # gigantic number to push unknowns to end

def load_chunks(folder: Path, exts):
    out = []
    if not folder.exists():
        return out
    for p in sorted(folder.glob("*"), key=lambda x: extract_index(x.name)):
        if p.suffix.lower() in exts:
            out.append(p)
    return out

# Load sentences and chunks
sentences = read_pdf_sentences(pdf_path)
st.subheader("📖 Extracted Sentences from PDF")
if sentences:
    st.write(f"Found **{len(sentences)}** sentences.")
    with st.expander("Show sentences"):
        for i, s in enumerate(sentences, 1):
            st.markdown(f"**{i}.** {s}")
else:
    st.info("No sentences extracted — either the PDF path is wrong or PyPDF2 is not installed.")

base_chunks = load_chunks(Path(base_dir), {".mp3", ".wav", ".m4a", ".ogg", ".flac"})
clone_chunks = load_chunks(Path(clone_dir), {".mp3", ".wav", ".m4a", ".ogg", ".flac"})

tabs = st.tabs(["🎙️ Cloned Voice Chunks", "🗣️ Base TTS Chunks"])
for tab, chunks, label in [
    (tabs[0], clone_chunks, "Cloned voice"),
    (tabs[1], base_chunks, "Base TTS")
]:
    with tab:
        if not chunks:
            st.warning(f"No audio files found in the selected folder for **{label}**.")
        else:
            st.success(f"Found {len(chunks)} chunk(s).")
            for i, p in enumerate(chunks, 1):
                st.markdown(f"**Sentence {extract_index(p.name)}** — `{p.name}`")
                try:
                    st.audio(p.read_bytes())
                except Exception:
                    st.error("Couldn't render audio preview.")
                if i < len(chunks):
                    st.divider()

def merge_chunks(chunks, out_path: Path, make_srt=True):
    if AudioSegment is None:
        st.error("pydub is not installed. Please install it (and ffmpeg) to enable merging.")
        return None, None
    if not chunks:
        st.error("No chunks to merge.")
        return None, None
    audio = None
    timestamps = []  # (start_ms, end_ms, sentence_text)
    cur_ms = 0
    for idx, p in enumerate(chunks, 1):
        seg = AudioSegment.from_file(p)
        if audio is None:
            audio = seg
        else:
            audio += seg
        start = cur_ms
        end = cur_ms + len(seg)
        cur_ms = end
        # Optional sentence text by index, best-effort
        sent_text = ""
        si = extract_index(p.name)
        if 1 <= si <= len(sentences):
            sent_text = sentences[si-1]
        timestamps.append((start, end, sent_text))
    # Export
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio.export(out_path, format=out_path.suffix.lstrip("."))
    srt_bytes = None
    if make_srt:
        def ms_to_ts(ms):
            h = ms // 3600000
            ms %= 3600000
            m = ms // 60000
            ms %= 60000
            s = ms // 1000
            ms %= 1000
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        lines = []
        for i, (start, end, txt) in enumerate(timestamps, 1):
            lines.append(str(i))
            lines.append(f"{ms_to_ts(start)} --> {ms_to_ts(end)}")
            lines.append(txt if txt else f"Sentence {i}")
            lines.append("")  # blank line
        srt_bytes = "\n".join(lines).encode("utf-8")
    return out_path, srt_bytes

st.divider()
st.header("🧩 Merge")
if st.button("Merge selected set now"):
    target = target_choice
    if target == "Cloned voice":
        chunks = clone_chunks
    else:
        chunks = base_chunks
    out_file = Path(output_name)
    out, srt = merge_chunks(chunks, out_file, make_srt=make_srt)
    if out:
        st.success(f"Merged {len(chunks)} chunks → **{out.name}** (saved in current working directory).")
        with open(out, 'rb') as f:
            st.download_button("Download merged audio", data=f, file_name=out.name)
    if srt:
        st.download_button("Download captions (SRT)", data=srt, file_name=out_file.with_suffix(".srt").name)

st.info("Tip: If the sentence numbering in filenames starts from 0 or is non-sequential, the app still sorts by the number it finds in each filename.")
