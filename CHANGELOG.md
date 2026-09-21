# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1]

Compatibility release for code written against 0.5.x. Packages that pinned `suthing>=0.5` without an upper bound broke on a fresh install of 0.6.0; with 0.6.1 they work unchanged. The shims below will be removed in 0.7, so pin `suthing>=0.6.1,<0.7` and move off them.

### Changed

- `strenum` is a dependency again. suthing does not use it, but code that imported `strenum` while only receiving it through suthing 0.5 failed with `ModuleNotFoundError` on 0.6.0.

### Deprecated

- `FileHandle.load(fpath=...)` is accepted again and emits `DeprecationWarning`; pass the path positionally.
- `Timer.mins` and `Timer.secs` are back and emit `DeprecationWarning`; use `Timer.elapsed` or `Timer.format()`.

## [0.6.0] - 2026-09-22

### Added

- `suthing.jsonl`: `iter_jsonl` (streaming, strict or skip-and-warn), `read_jsonl` returning `(rows, errors)` with line numbers, and `write_jsonl` (append and atomic modes). All accept compressed files.
- `suthing.hashing`: `canonical_json`, `stable_hash`, `text_hash`, `bytes_hash`, `file_hash`, `tree_hash`. `stable_hash(obj)` is byte-identical to `sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")))`, so existing stored hashes stay valid.
- `suthing.fs`: `atomic_write` / `atomic_open` (same-directory temp file + `os.replace`; keeps permissions; optional `fsync`), `open_compressed`, `expand_path`.
- `.bz2` and `.xz` compression, plus `.zst` via the new `zstd` extra.
- `FileHandle.load_resource(package, name)` for data shipped inside a package, and `FileHandle.iter` for streaming JSONL, text lines and CSV chunks.
- TSV support, `.jsonl` / `.ndjson` extensions, and a `.env` writer.
- `Timer`: live `elapsed` inside the block, `elapsed_ms`, `format(digits)`, an optional `label` and `log` callback, and decorator use.
- `diff()` returning a `Difference` (path, expected, actual, reason) for every mismatch, with `rel_tol` / `abs_tol`, `ignore_order` and `max_diffs`.
- `Profiler` / `profiled`: opt-in profiling through a context variable, so decorated functions no longer need a `_profiler` argument; `Profiler.summary()` gives count, total, mean, median and max per key.
- `to_jsonable`, `batched`, `slugify`, `env_flag`, `load_env`, `setup_logging`, `utc_now_iso`, `format_duration`.
- `py.typed` marker, Python 3.13 classifier, and a pytest step in CI.

### Changed

- **Breaking:** `FileHandle.load(path, *, how=None, **kwargs)` takes one path. Package data moves to `load_resource(package, name)`, and the `fpath=` keyword is gone. Unexpected keyword arguments raise `TypeError` (only CSV/TSV forward them to pandas).
- **Breaking:** an unknown extension raises `ValueError` instead of falling back to text. `how=` now overrides the extension; before, it was ignored whenever the extension was recognised.
- **Breaking:** `.jsonld` is read and written as JSON (JSON-LD). JSON Lines use `.jsonl` / `.ndjson`, and `FileType.JSONLD` is renamed `FileType.JSONL`.
- **Breaking:** `equals` compares lengths. It used `zip` and reported `[1, 2]` and `[1]` as equal. It now also compares sets as sets, treats `nan` as equal to `nan`, and no longer logs at ERROR level.
- **Breaking:** loading a dotenv file returns a `dict` and leaves `os.environ` alone; use `load_env` to export it.
- **Breaking:** YAML loads with `safe_load`. Dumps keep key order and write non-ASCII text as-is. Enums, tuples, paths, `Decimal` and similar values are written as plain YAML instead of `!!python/...` tags.
- JSON dumps write non-ASCII text as-is and convert enums, dates, UUIDs, paths and numpy values through `to_jsonable`.
- `FileHandle.dump` writes atomically by default, returns the written path, and takes `mkdir=`. It raises `TypeError` on a value the format cannot hold instead of writing an empty or `repr`'d file. Text into a `.gz` file works; it used to raise `TypeError`.
- pandas is imported only when a CSV/TSV file is read or written.

### Removed

- **Breaking:** `Timer.mins` and `Timer.secs` (restored as deprecated in 0.6.1).
- **Breaking:** `secureit`, `timeit`, `Report`, `Return`, `SProfiler`, `profile` and the `suthing.decorate` module. Use `Profiler` / `profiled` for profiling and `Timer` for timing.
- Unused runtime dependencies `dataclass-wizard` and `strenum` (`strenum` restored in 0.6.1). `mkdocs-gen-files` moves to the `docs` dependency group.

## [0.5.1] - 2026-02-01

### Changed

- Require Python ≥3.11 (drop 3.10).
- Drop the upper pin on `dataclass-wizard`.
- Add `ty` to the `dev` dependency group for type checking.

## [0.5.0] - 2025-11-09

### Removed

- **Breaking:** remove the `suthing.connection` package (`ConnectionConfig`, `ConfigFactory`, and DB/WSGI connection configs). Connection configuration no longer ships with this library.
- Dedicated pytest GitHub Actions workflow; checks run through pre-commit.

## [0.4.0] - 2025-05-01

Historical release that reshaped the connection-configuration API (URL/`username`/`password` parameters, factory changes). That API was removed entirely in [0.5.0](#050---2025-11-09).

## [0.3.0] - 2025-01-15

- published on pypi

## [0.2.4] - 2023-09-01

- FileHandle
  - added support for reading .env files and pushing them to environment

## [0.2.3] - 2023-08-30

- switched to python 3.10
- FileHandle
  - added support for reading txt files by default
  - if a single argument to FileHandle.load() is not named it is interpreted as filepath
