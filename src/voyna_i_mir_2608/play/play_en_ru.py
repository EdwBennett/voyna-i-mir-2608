
from typing import Callable, Optional
import voyna_i_mir_2608/play_ru voyna_i_mir_2608/play_ru
import voyna_i_mir_2608/play_call_response voyna_i_mir_2608/play_call_response

def play_en_ru(id: int) -> None:
    fn_call: Callable[[], None] = None
    fn_response: Callable[[], None] = play_ru(id)
    play_call_response(None, play_ru)
    pass
