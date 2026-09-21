# API Reference

Every public name is importable from `suthing` directly.

## Core Modules

- [File Handling](core.md#file-handling) - `FileHandle`, `FileType`: format-aware load/dump with compression
- [JSON Lines](core.md#json-lines) - `iter_jsonl`, `read_jsonl`, `write_jsonl`
- [File System](core.md#file-system) - `atomic_write`, `atomic_open`, `open_compressed`, `expand_path`
- [Timing](core.md#timing) - `Timer`, `format_duration`, `utc_now_iso`
- [Profiling](core.md#profiling) - `Profiler`, `profiled`
- [Comparison](core.md#comparison) - `diff`, `equals`
- [Hashing](core.md#hashing) - `stable_hash`, `canonical_json`, `text_hash`, `file_hash`, `tree_hash`
- [JSON Conversion](core.md#json-conversion) - `to_jsonable`
- [Iteration](core.md#iteration) - `batched`
- [Text](core.md#text) - `slugify`
- [Environment](core.md#environment) - `env_flag`, `load_env`
- [Logging](core.md#logging) - `setup_logging`

## Quick Links

- [Getting Started](../getting_started/quickstart.md) - Basic usage examples
- [Examples](../examples.md) - Practical use cases
- [Contributing](../contributing.md) - How to contribute
