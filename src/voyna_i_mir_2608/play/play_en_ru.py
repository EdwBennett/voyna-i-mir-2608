"""Top-level driver: play, print, or render English/Russian sentence pairs.

Also runnable as a script:

    python -m voyna_i_mir_2608.play.play_en_ru <id> <delay> [clause] [-o OUTPUT | -t | -i]
"""

import subprocess
from collections.abc import Callable
from typing import Optional

from voyna_i_mir_2608.db.sentence_pairs import parse_id_list
from voyna_i_mir_2608.play import play
from voyna_i_mir_2608.play.play_lang import play_en, play_ru, print_en, print_ru, render_en, render_ru
from voyna_i_mir_2608.play.play_wait import play_wait, play_wait_key
from voyna_i_mir_2608.say.say import SAMPLE_RATE, silence


def play_en_ru(
    id_: str,
    delay: int,
    clause: Optional[int] = None,
    output: Optional[str] = None,
    text_only: bool = False,
    interactive: bool = False,
) -> None:
    """Play, print, or render (to mp3) the English/Russian pairs matching `id_`.

    `id_` is a printer-style spec (e.g. "1,3,5-8") parsed by `parse_id_list`.
    `output`, `text_only`, and `interactive` are mutually exclusive; with none
    set, each pair is spoken aloud (English, then a `delay`-second pause, then
    Russian). With `interactive` set, the pause instead waits for the space
    bar to be pressed.
    """
    if sum((output is not None, text_only, interactive)) > 1:
        raise ValueError("output, text_only, and interactive are mutually exclusive")

    ids = parse_id_list(id_)

    if output is not None:
        _render_to_mp3(ids, delay, clause, output)
        return

    if text_only:
        for pair_id in ids:
            play(print_en(pair_id, clause), None, print_ru(pair_id, clause))
        return

    for pair_id in ids:
        fn_call: Callable[[], None] = play_en(pair_id, clause)
        fn_wait: Callable[[], None] = play_wait_key() if interactive else play_wait(delay)
        fn_response: Callable[[], None] = play_ru(pair_id, clause)
        play(fn_call, fn_wait, fn_response)


def _render_to_mp3(ids: list[int], delay: int, clause: Optional[int], output: str) -> None:
    """Synthesize every id's en/ru pair (with delay silence) and encode straight to mp3.

    Skips live playback entirely, so this only takes as long as synthesis and
    encoding, not the real-time duration of the audio and delay.
    """
    if not output.endswith(".mp3"):
        raise ValueError(f"Output path must end with .mp3: {output}")

    delay_silence = silence(delay)
    audio = b"".join(
        render_en(id_, clause) + delay_silence + render_ru(id_, clause) + delay_silence
        for id_ in ids
    )

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
    import argparse

    parser = argparse.ArgumentParser(
        description="Play (or render to mp3) English/Russian sentence pairs."
    )
    parser.add_argument("id", help="Sentence pair id or id spec, e.g. '1,3,5-8'")
    parser.add_argument("delay", type=int, help="Delay in seconds between English and Russian audio")
    parser.add_argument(
        "clause", type=int, nargs="?", default=None, help="Optional clause index within the sentence"
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "-o", "--output",
        default=None,
        help="Write to this .mp3 path instead of playing live",
    )
    output_group.add_argument(
        "-t", "--text-only",
        action="store_true",
        help="Print the sentence pairs with no audio and no delays",
    )
    output_group.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Wait for the space bar instead of the delay between English and Russian audio",
    )
    args = parser.parse_args()

    play_en_ru(
        args.id,
        delay=args.delay,
        clause=args.clause,
        output=args.output,
        text_only=args.text_only,
        interactive=args.interactive,
    )
