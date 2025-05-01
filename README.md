# SUThing <img src="docs/assets/favicon.ico" alt="suthing logo" style="height: 32px; width:32px;"/>

SUThing /ˈsu.θɪŋ/ or /ˈsʌ.θɪŋ/ (Some Useful Things) is a collection of useful classes and decorators.  

A Python utility package providing tools for file handling, timing, profiling, and data comparison.

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
[![PyPI version](https://badge.fury.io/py/suthing.svg)](https://badge.fury.io/py/suthing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://github.com/growgraph/suthing/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/growgraph/suthing/actions/workflows/pre-commit.yml)
[![pytest](https://github.com/growgraph/suthing/actions/workflows/pytest.yml/badge.svg)](https://github.com/growgraph/suthing/actions/workflows/pytest.yml)

## Features

- **File Handling**: one-line file reading/wriing with file format infererence from provided extension (YAML, JSON, CSV, pickle, gz etc.)
- **Performance Measurement**: Simple timer utilities and profiling decorators
- **Data Comparison**: Deep comparison of nested data structures
- **Error Handling**: Decorators for secure function execution and error tracking

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

# Read YAML file
data = FileHandle.load(fpath="config.yaml")

# Write compressed JSON
# file type inferred from extension
FileHandle.dump(data, "output.json.gz")
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
from suthing import profile, SProfiler

profiler = SProfiler()

@profile(_argnames="input_size")
def my_function(input_size):
    # Function code
    pass

# Run with profiler
my_function(input_size=100, _profiler=profiler)

# View results
stats = profiler.view_stats()
```

### Deep Comparison

```python
from suthing import equals

# Compare nested structures
result = equals(complex_dict1, complex_dict2)
```

## Requirements

- Python 3.10+
- pandas
- PyYAML
- python-dotenv

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.