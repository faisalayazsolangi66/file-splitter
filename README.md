# File Splitter

Split a large file into fixed-size chunks.

## Requirements

- Python 3.8+
- No third-party packages (standard library only)

## Usage

```bash
python3 main.py <file> [--size 10MB] [--output-dir DIR]
python3 main.py <file> --join [--output FILE]
```

Chunk sizes accept plain bytes or suffixes: `1024`, `10KB`, `5MB`, `1GB`. Chunks are named `<file>.part001`, `<file>.part002`, … and `--join` reassembles them.

## Example

```bash
$ python3 main.py big-video.mp4 --size 5MB
Wrote big-video.mp4.part001 (5242880 bytes)
Wrote big-video.mp4.part002 (5242880 bytes)
Wrote big-video.mp4.part003 (1048576 bytes)

Split big-video.mp4 (11534336 bytes) into 3 chunk(s) of up to 5242880 bytes in big-video.mp4.chunks/
```

## License

MIT — see [LICENSE](LICENSE).
