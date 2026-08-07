# voyna-i-mir-2608

Bilingual Russian/English sentence-pair audio drills: play, print, or render
to mp3 an English sentence followed by its Russian translation, with a pause
(or interactive space-bar advance) in between.

## Install

```bash
uv tool install git+https://github.com/EdwBennett/voyna-i-mir-2608.git
```

This installs the `voyna-i-mir-2608` command in an isolated environment. To
pick up new commits later, re-run the same command (or `uv tool upgrade
voyna-i-mir-2608`).

## Host setup

The Python package alone isn't enough to hear anything — it shells out to a
few system tools that aren't pip-installable, so these need to be set up
once per machine you actually want to play audio on:

- **ffmpeg** — used when rendering to an mp3 file (`-o`).
- **aplay** (ALSA) — used for live playback. Check/install:
  ```bash
  command -v aplay || sudo dnf install -y alsa-utils
  ```
- **piper** — the text-to-speech engine. Check/install:
  ```bash
  command -v piper || uv tool install piper-tts
  ```
  This installs the binary to `~/.local/bin/piper`, the path this project
  expects.
- **Voice models** — three `.onnx` + `.onnx.json` pairs, downloaded from the
  [`rhasspy/piper-voices`](https://huggingface.co/rhasspy/piper-voices)
  HuggingFace repo into `~/.local/share/piper-voices/`, mirroring its
  directory structure:

  | Language | Voice  | Path |
  | -------- | ------ | ---- |
  | English  | amy    | `en/en_US/amy/medium/en_US-amy-medium.onnx{,.json}` |
  | Russian  | denis  | `ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx{,.json}` |
  | Russian  | irina  | `ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx{,.json}` |

  Example for one pair:
  ```bash
  mkdir -p ~/.local/share/piper-voices/en/en_US/amy/medium
  cd ~/.local/share/piper-voices/en/en_US/amy/medium
  curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
  curl -LO https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
  ```
  Repeat for the `ru_RU/denis` and `ru_RU/irina` paths above.

Sanity check once everything's in place:

```bash
echo "привет" | ~/.local/bin/piper \
  --model ~/.local/share/piper-voices/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx \
  --config ~/.local/share/piper-voices/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json \
  --output_raw | aplay -r 22050 -f S16_LE -t raw -c1
```

## Usage

```bash
voyna-i-mir-2608 <id> <delay> [clause] [--ru-voice {irina,denis}] [-o OUTPUT | -t | -i]
```

- `id` — a sentence pair id or id spec, e.g. `1`, `1,3,5-8`.
- `delay` — seconds of pause between the English and Russian audio.
- `clause` — optional clause index within the sentence.
- `--ru-voice` — Russian voice to use (default: `denis`).
- `-o, --output PATH` — render to an mp3 file instead of playing live.
- `-t, --text-only` — print the sentence pairs with no audio and no delays.
- `-i, --interactive` — wait for the space bar instead of the delay; press
  `r` after the Russian audio to replay it.

Example:

```bash
voyna-i-mir-2608 1,3,5-8 3 --ru-voice irina
```
