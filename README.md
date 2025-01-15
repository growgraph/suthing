# SUThing

SUThing /ˈsu.θɪŋ/ or /ˈsʌ.θɪŋ/ (Some Useful Things) is a collection useful classes and decorators.  

A Python utility package providing tools for file handling, timing, profiling, and data comparison.

## Features

- **File Handling**: Flexible interface for reading/writing multiple file formats (YAML, JSON, CSV, pickle, etc.)
- **Performance Measurement**: Simple timer utilities and profiling decorators
- **Data Comparison**: Deep comparison of nested data structures
- **Error Handling**: Decorators for secure function execution and error tracking

## Installation

```bash
pip install suthing
```

## Usage Examples

### File Handling

```python
from suthing.file_handle import FileHandle, FileType

# Read YAML file
data = FileHandle.load(fpath="config.yaml")

# Write compressed JSON
FileHandle.dump(data, "output.json.gz", how=FileType.JSON)
```

### Timing Code

```python
from suthing.timer import Timer

with Timer() as t:
    # Your code here
    pass
print(f"Execution took {t.elapsed_str}")
```

### Profiling Functions

```python
from suthing.decorate import profile, SProfiler

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
from suthing.compare import equals

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