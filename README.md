# SUThing <img src="docs/assets/favicon.ico" alt="suthing logo" style="height: 32px; width:32px;"/>

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

## Documentation
Full documentation is available at: [growgraph.github.io/suthing](https://growgraph.github.io/suthing)

## Installation

```bash
pip install suthing
```

## Usage Examples

### File Handling

```python
from suthing import FileHandle, FileType

# format inferred from the extension
data = FileHandle.load("config.yaml")

# compressed by suffix, written atomically
FileHandle.dump(data, "output.json.gz")

# data shipped inside a package
defaults = FileHandle.load_resource("mypkg.data", "defaults.yaml")

# explicit format for an unrecognised extension
secret = FileHandle.load("token.secret", how=FileType.TXT)
```

### Timing Code

```python
from suthing import Timer

with Timer() as t:
    # Your code here
    pass
print(f"Execution took {t.elapsed_str}")
```

### Profiling Functions

```python
from suthing import Profiler, profiled


@profiled(key_args="input_size")
def my_function(input_size): ...


with Profiler() as prof:
    my_function(100)

stats = prof.summary()  # {"my_function(input_size=100)": ProfileStats(...)}
```

### Deep Comparison

```python
from suthing import diff, equals

equals(expected, actual)  # bool
for d in diff(expected, actual):  # where they differ
    print(d)  # $.users[1].name: values differ (expected='Bob', actual='Rob')
```

## Requirements

- Python 3.11+
- pandas (imported only for CSV/TSV)
- PyYAML
- python-dotenv
- optional: `zstandard` for `.zst` files (`pip install "suthing[zstd]"`)

## Development

```bash
uv sync --group dev
uv run pytest test
uv run ty check suthing test
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. See [Contributing](docs/contributing.md) for the full workflow.
