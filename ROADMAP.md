# Roadmap

This document tracks the planned evolution of IELTS Speaking Coach from a
simple practice tool into a full ML-powered speaking coach.

## v1.0 — Current

- [x] Question banks for Parts 1, 2, and 3
- [x] Timers matching official IELTS structure
- [x] Audio recording of user responses
- [x] CLI interface

## v2.0 — Speech-to-text

Transcribe recorded answers automatically so users can read back what they
actually said.

- [ ] Integrate OpenAI Whisper (local or API)
- [ ] Save transcripts alongside audio files
- [ ] Word count and speaking rate (words per minute)

## v3.0 — LLM-based feedback

Use a language model to evaluate the transcript across the four official
IELTS speaking criteria:

- [ ] Fluency and coherence
- [ ] Lexical resource (vocabulary range)
- [ ] Grammatical range and accuracy
- [ ] Pronunciation (initial heuristic)

Output a band-score estimate and concrete suggestions for improvement.

## v4.0 — Pronunciation model

Replace the heuristic pronunciation score with a custom ML model.

- [ ] Curate a dataset of native and non-native English speech samples
- [ ] Train a model to score pronunciation quality
- [ ] Compare against off-the-shelf options as a baseline

## v5.0 — Progress tracking and web UI

- [ ] Store session history and band-score estimates over time
- [ ] Visualize improvement curves
- [ ] Move from CLI to a simple web interface (Flask or FastAPI + a basic
      frontend)

---

This roadmap is intentionally ambitious — it's the project I want this to
become, not what it is today. Each version is a learning milestone in my
path toward Machine Learning Engineering.
