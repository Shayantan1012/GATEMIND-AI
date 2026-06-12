import sys
import unittest
from pathlib import Path

from app.config import Config


class TeeStream:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, value):
        for stream in self.streams:
            stream.write(value)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


if __name__ == "__main__":
    output_folder = Path(Config.TEST_OUTPUT_FOLDER)
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "latest-tests.log"

    with output_file.open("w", encoding="utf-8") as file_stream:
        result = unittest.TextTestRunner(
            stream=TeeStream(sys.stderr, file_stream),
            verbosity=2,
        ).run(unittest.defaultTestLoader.discover("tests"))

    raise SystemExit(not result.wasSuccessful())
