#!/usr/bin/env python3
"""
Speech-to-Text using OpenAI Whisper (runs locally, completely free).

Usage:
    python speech_to_text.py                    # Record 5 seconds, transcribe
    python speech_to_text.py --duration 10      # Record 10 seconds
    python speech_to_text.py --file audio.wav   # Transcribe existing file
    python speech_to_text.py --model medium     # Use medium model (more accurate)
    python speech_to_text.py --list-devices     # List audio input devices
    python speech_to_text.py --device 1         # Use specific input device

Models (accuracy vs speed tradeoff):
    tiny    - Fastest, least accurate (~1GB VRAM)
    base    - Fast, decent accuracy (~1GB VRAM)
    small   - Good balance (~2GB VRAM)
    medium  - High accuracy (~5GB VRAM)
    large   - Best accuracy (~10GB VRAM)
    turbo   - Fast + accurate, recommended if you have GPU

First run will download the model (~74MB for tiny, ~1.5GB for medium).
"""

import argparse
import sys
import tempfile
import os
from pathlib import Path

def list_audio_devices():
    """List available audio input devices."""
    import sounddevice as sd
    print("\nAvailable audio input devices:")
    print("-" * 50)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            marker = " (default)" if i == sd.default.device[0] else ""
            print(f"  [{i}] {device['name']}{marker}")
    print()

def record_audio(duration: float, device: int = None) -> str:
    """Record audio from microphone and save to temp file."""
    import sounddevice as sd
    from scipy.io import wavfile

    sample_rate = 16000  # Whisper expects 16kHz

    print(f"Recording for {duration} seconds... (speak now)")

    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            device=device
        )
        sd.wait()  # Wait until recording is finished
    except Exception as e:
        print(f"Error recording audio: {e}")
        print("\nTry listing devices with --list-devices and selecting one with --device")
        sys.exit(1)

    print("Recording complete.")

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wavfile.write(temp_file.name, sample_rate, audio)

    return temp_file.name

def transcribe(audio_path: str, model_name: str = "base") -> str:
    """Transcribe audio file using Whisper."""
    import whisper

    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print("Transcribing...")
    result = model.transcribe(audio_path)

    return result["text"].strip()

def main():
    parser = argparse.ArgumentParser(
        description="Speech-to-Text using OpenAI Whisper (local, free)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Recording duration in seconds (default: 5)"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Transcribe existing audio file instead of recording"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="base",
        choices=["tiny", "tiny.en", "base", "base.en", "small", "small.en",
                 "medium", "medium.en", "large", "large-v2", "large-v3", "turbo"],
        help="Whisper model to use (default: base)"
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices"
    )
    parser.add_argument(
        "--device",
        type=int,
        help="Audio input device index (use --list-devices to see options)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Write transcription to file instead of stdout"
    )

    args = parser.parse_args()

    if args.list_devices:
        list_audio_devices()
        return

    # Get audio file path
    temp_file = None
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        audio_path = args.file
    else:
        audio_path = record_audio(args.duration, args.device)
        temp_file = audio_path

    try:
        # Transcribe
        text = transcribe(audio_path, args.model)

        # Output
        if args.output:
            Path(args.output).write_text(text, encoding='utf-8')
            print(f"Transcription saved to: {args.output}")
        else:
            print("\n" + "=" * 50)
            print("TRANSCRIPTION:")
            print("=" * 50)
            print(text)
            print("=" * 50 + "\n")

    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    main()
