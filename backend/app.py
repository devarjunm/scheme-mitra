"""Retired insecure MVP entry point.

The previous standard-library HTTP adapter was removed. Use ``python run.py`` to
start the FastAPI application defined in ``backend.api.main``.
"""


def main() -> None:
    raise SystemExit("This legacy Scheme Mitra server has been retired. Start the FastAPI app with `python run.py`.")


if __name__ == "__main__":
    main()
