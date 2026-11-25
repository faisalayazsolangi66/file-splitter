#!/usr/bin/env python3
"""Split a large file into fixed-size chunks.

Usage:
    python3 main.py <file> --size 10MB [--output-dir chunks] [--join]
"""
import argparse
import re
from pathlib import Path

CHUNK_SIZE = 1024 * 1024


def parse_size(text: str) -> int:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KMGT]?B?)?", text.strip(), re.I)
    if not match:
        raise argparse.ArgumentTypeError(
            f"invalid size: {text!r} (examples: 1024, 10KB, 5MB, 1GB)")
    value, unit = float(match.group(1)), (match.group(2) or "B").upper()
    multipliers = {"B": 1, "KB": 1024, "MB": 1024 ** 2,
                   "GB": 1024 ** 3, "TB": 1024 ** 4,
                   "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}
    return int(value * multipliers[unit])


def split_file(source: Path, chunk_size: int, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    total = source.stat().st_size
    parts = []
    with source.open("rb") as src:
        index = 1
        while True:
            data = src.read(chunk_size)
            if not data:
                break
            part = output_dir / f"{source.name}.part{index:03d}"
            part.write_bytes(data)
            parts.append(part)
            print(f"Wrote {part.name} ({len(data)} bytes)")
            index += 1
    print(f"\nSplit {source} ({total} bytes) into {len(parts)} chunk(s) "
          f"of up to {chunk_size} bytes in {output_dir}/")
    return parts


def join_parts(source: Path, output: Path, chunk_dir: Path = None):
    """Reassemble a file previously split by this tool."""
    candidates = []
    if chunk_dir is not None:
        candidates.append(chunk_dir)
    candidates.append(source.parent)
    candidates.append(source.with_suffix(source.suffix + ".chunks"))
    parts = []
    for directory in candidates:
        parts = sorted(directory.glob(f"{source.name}.part*"))
        if parts:
            break
    if not parts:
        raise SystemExit(f"No chunks found matching {source.name}.part* "
                         f"(looked in {', '.join(str(c) for c in candidates)})")
    with output.open("wb") as out:
        for part in parts:
            out.write(part.read_bytes())
            print(f"Joined {part.name}")
    print(f"\nReassembled {len(parts)} chunk(s) into {output} "
          f"({output.stat().st_size} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="Split a large file into fixed-size chunks.")
    parser.add_argument("file", type=Path, help="File to split (or join)")
    parser.add_argument("--size", type=parse_size, default=10 * 1024 * 1024,
                        help="Chunk size, e.g. 1024, 10KB, 5MB, 1GB "
                             "(default: 10MB)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Where to write chunks (default: <file>.chunks/); "
                             "for --join, where to look for them")
    parser.add_argument("--join", action="store_true",
                        help="Reassemble .partNNN chunks back into one file")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output file for --join (default: original name)")
    args = parser.parse_args()
    if args.join:
        output = args.output or args.file
        join_parts(args.file, output, chunk_dir=args.output_dir)
        return
    if not args.file.is_file():
        parser.error(f"not a file: {args.file}")
    if args.size <= 0:
        parser.error("--size must be greater than 0")
    output_dir = args.output_dir or args.file.with_suffix(args.file.suffix + ".chunks")
    split_file(args.file, args.size, output_dir)


if __name__ == "__main__":
    main()
