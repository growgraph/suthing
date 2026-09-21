# Welcome to Suthing

SUThing /ˈsu.θɪŋ/ or /ˈsʌ.θɪŋ/ (Some Useful Things) is a collection of small, dependable utilities.  

A Python utility package providing tools for file handling, timing, profiling, data comparison and hashing.

![Python](https://img.shields.io/badge/python-%3E=3.11-blue?logo=python)
[![PyPI version](https://badge.fury.io/py/suthing.svg)](https://badge.fury.io/py/suthing)
[![PyPI Downloads](https://static.pepy.tech/badge/suthing)](https://pepy.tech/projects/suthing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://github.com/growgraph/suthing/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/growgraph/suthing/actions/workflows/pre-commit.yml)

## Features

- **File Handling**: one-line reading and writing with the format inferred from the extension (YAML, JSON, JSON Lines, CSV/TSV, text, dotenv, pickle), transparent `.gz`/`.bz2`/`.xz`/`.zst` compression, atomic writes and streaming reads
- **Timing and Profiling**: a `Timer` context manager/decorator and opt-in function profiling with per-key statistics
- **Data Comparison**: deep `diff` of nested structures that reports the path of every difference, with numeric tolerance and order-insensitive matching
- **Hashing**: stable hashes of JSON-like values, text, files and directory trees
- **Small Helpers**: `batched`, `slugify`, `to_jsonable`, `env_flag`, `setup_logging`, `utc_now_iso`

## Quick Start

```python
from suthing import FileHandle, Timer, equals

# Read a file
data = FileHandle.load("config.yaml")

# Time your code
with Timer() as t:
    # Your code here
    pass
print(f"Execution took {t.elapsed_str}")

# Compare complex structures
result = equals(dict1, dict2)
```

## Documentation

Explore the documentation to learn more about Suthing's features:

- [Getting Started](getting_started/quickstart.md) - Learn how to install and use Suthing
- [API Reference](reference/index.md) - Complete API documentation
- [Examples](examples.md) - Code examples and usage patterns

## Requirements

- Python 3.11+
- pandas (imported only for CSV/TSV)
- PyYAML
- python-dotenv
- optional: `zstandard` for `.zst` files (`pip install "suthing[zstd]"`)

## Contributing

We welcome contributions! Please check out our [Contributing Guide](contributing.md) for details on how to get started.
