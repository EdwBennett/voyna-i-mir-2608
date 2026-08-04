"""Package entry point for `python -m voyna_i_mir_2608`.

Delegates directly to `voyna_i_mir_2608.cli.main` and exits with its
return code.

Usage:
    python -m voyna_i_mir_2608

No external dependencies required.
"""

from voyna_i_mir_2608.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
    