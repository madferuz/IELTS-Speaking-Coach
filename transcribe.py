"""Speech-to-text transcription using OpenAI Whisper.

Roadmap v2.0 — transcribes a recorded IELTS answer into text so the
response can be read back and, later, scored by the feedback pipeline.
"""

from pathlib import Path


def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """Transcribe a recorded audio answer to text.

    Args:
        audio_path: Path to the recorded audio file (e.g. a .wav or .mp3).
        model_name: Whisper model size — "tiny", "base", "small", "medium",
            or "large". Larger models are more accurate but slower.

    Returns:
        The transcribed text of the spoken answer.

    Raises:
        FileNotFoundError: If audio_path does not point to an existing file.
    """
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # TODO: integrate OpenAI Whisper.
    #   import whisper
    #   model = whisper.load_model(model_name)
    #   result = model.transcribe(str(path))
    #   return result["text"].strip()
    raise NotImplementedError("Whisper integration not yet implemented.")


if __name__ == "__main__":
    # Quick manual smoke test once implemented:
    # print(transcribe_audio("sample_answer.wav"))
    pass
