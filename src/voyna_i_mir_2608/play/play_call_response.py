"""

"""

from typing import Callable, Optional

def play(fn_call: Optional[Callable[[], None]], fn_response: Optional[Callable[[], None]]) -> None:
    """Executes a function call followed by its response function, allowing either to be None."""
    if fn_call is not None:
        fn_call()
    if fn_response is not None:
        fn_response()
