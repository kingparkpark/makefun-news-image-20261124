#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261124.

Writes the finished front page to /output/entry.png, byte for byte.
The image is built ahead of time (see render.py + stories.json in this
repository) and ships as news.png.b64, the base64 text encoding of the
PNG, so the whole entry travels as plain text files. This program only
decodes and copies it, so two runs always produce the same bytes.
No network, no randomness, no wall-clock use.
"""
import base64
import os
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "news.png.b64")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(src, "r", encoding="ascii") as f:
        data = base64.b64decode(f.read())
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        sys.exit("decoded news.png.b64 is not a PNG file")
    with open(dst, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
