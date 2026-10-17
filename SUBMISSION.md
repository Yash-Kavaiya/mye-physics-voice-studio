# Mye Physics Voice Studio: AssemblyAI Voice Hackathon submission

**Tagline:** Physics lessons that check their own voice.

**Repo:** https://github.com/Yash-Kavaiya/mye-physics-voice-studio
**Demo video:** https://youtu.be/QFNoym-jpbY (4:41, 1080p)
**Team:** Yash Kavaiya (solo)

## What it does
Mye Physics Voice Studio turns a physics script into a fully animated, narrated, captioned lesson, and it **verifies every line it speaks**. Each narration line is synthesised with **AssemblyAI Text-to-Speech**, transcribed straight back with **AssemblyAI Universal STT**, and scored by word error rate against the script, with math-aware normalisation so "2πi" counts as "two pi i". Takes above 10% WER are regenerated automatically. A line that still fails after three takes is flagged for a human instead of reaching students. The same STT word timestamps drive the ManimGX animation cues and produce **word-timed SRT captions** for free. ffmpeg then concatenates the sections, normalises loudness and adds the watermark.

A second mode, **Talk to your teacher**, lets a student ask a doubt out loud. The **Voice Agent API** transcribes it in real time, writes a short answer and speaks it in the teacher's voice. Voice Studio verifies the answer and renders it as an animated, captioned clip. In our run the first answer audio arrived 1.14 s after the question ended.

## Why it matters
I run Mye Physics, a YouTube channel for B.Sc and M.Sc students. A narrated lesson used to take hours. TTS made that faster but added a silent risk: a misread symbol ships to thousands of students. Voice Studio makes TTS trustworthy for education, and the captions make every lesson accessible.

## AssemblyAI features used
- **Text-to-Speech:** Voice Agent API voices (`michael`). Each line is synthesised verbatim through the documented `greeting` field, which is sent straight to TTS, with word timings from `transcript.agent.delta`.
- **Universal-3.5 Pro pre-recorded STT:** used for verification and word timestamps, with `keyterms_prompt` for physics vocabulary.
- **Voice Agent API:** streaming STT, LLM and TTS with turn detection and keyterms, for spoken Q&A.
- **LLM Gateway (optional):** `--topic` generates the lesson script.

## Results from the demo run
- 26 narration lines, 28 TTS takes and 4.3 minutes of AssemblyAI speech, with a mean WER of 3.2%.
- The loop caught a real error: "a one over z minus a term" kept coming back as "a 1/ term", so after 3 takes that line was flagged for review.
- The Q&A answer had a WER of 1.6%, and its audio started 1.14 s after the question ended.
- The demo video itself was produced end to end by the pipeline.

## How we built it
Python with `websockets` and `requests` against AssemblyAI's documented endpoints. ManimGX does the animation in a light theme with AssemblyAI colours and Latin Modern type, and equations are drawn with Write. ffmpeg handles concat, loudnorm and the watermark. A Gradio UI offers mic input, a single verified line, and a full lesson build.

## What's next
Swap to AssemblyAI's standalone TTS-1 when it launches (it's a one-file change), add a pronunciation dictionary for symbols, turn on LLM Gateway topic-to-script, and publish weekly lessons on Mye Physics.
