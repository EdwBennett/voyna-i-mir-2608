"""Render Russian sentences from the bundled dataset to a single mp3.

Each sentence is spoken in the denis voice with a 1-second silence between
entries (render_ru's own 0.5s lead-in on each clip means the actual gap
heard is ~1.5s, matching play_en_ru's convention).

Usage:
    uv run python scripts/make_ru_mp3.py -o ru_sentences.mp3
    uv run python scripts/make_ru_mp3.py 1,3,5-8 -o subset.mp3
"""

from __future__ import annotations

import argparse
import subprocess

from voyna_i_mir_2608.db.sentence_pairs import SentencePairs, parse_id_list
from voyna_i_mir_2608.play.play_lang import JSON_PATH, render_ru
from voyna_i_mir_2608.say.say import SAMPLE_RATE, silence

GAP_SECONDS = 1.0
VOICE = "denis"


def make_ru_mp3(ids: str | None, output: str) -> None:
    """Render each Russian sentence (`ids`, or all in the dataset if None) to `output`.

    `ids` is a printer-style id spec (e.g. "1,3,5-8") parsed by `parse_id_list`.
    """
    if not output.endswith(".mp3"):
        raise ValueError(f"Output path must end with .mp3: {output}")

    if ids is None:
        id_list = [pair.id for pair in SentencePairs(JSON_PATH)]
    else:
        id_list = parse_id_list(ids)

    gap = silence(GAP_SECONDS)
    audio = b"".join(render_ru(id_, voice=VOICE) + gap for id_ in id_list)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "s16le",
        "-ar", str(SAMPLE_RATE),
        "-ac", "1",
        "-i", "-",
        output,
    ]
    subprocess.run(ffmpeg_cmd, input=audio, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Render Russian sentences (denis voice) to a single mp3, 1s gaps between."
    )
    parser.add_argument(
        "ids", nargs="?", default=None, help="Id spec, e.g. '1,3,5-8' (default: all sentences)"
    )
    parser.add_argument("-o", "--output", required=True, help="Output .mp3 path")
    args = parser.parse_args()

    make_ru_mp3(args.ids, args.output)
