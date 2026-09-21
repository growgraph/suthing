# Quick Start

This guide covers the main features with short examples.

## File Handling

The format comes from the file extension, and a compression suffix (`.gz`, `.bz2`, `.xz`, `.zst`) is handled transparently:

```python
from suthing import FileHandle

data = FileHandle.load("config.yaml")
FileHandle.dump(data, "out/config.json.gz", mkdir=True)  # atomic by default

# data files shipped inside a package
defaults = FileHandle.load_resource("mypkg.data", "defaults.yaml")
```

An unknown extension is an error; pass `how=` to choose the format explicitly:

```python
from suthing import FileType

notes = FileHandle.load("notes.secret", how=FileType.TXT)
```

## Timing

```python
from suthing import Timer

with Timer() as t:
    result = some_expensive_operation()
print(f"Operation took {t.elapsed_str}")

# or log on exit
import logging

with Timer("ingest", log=logging.getLogger(__name__).info):
    ingest()
```

## Profiling Functions

Decorated functions are timed only while a `Profiler` is active:

```python
from suthing import Profiler, profiled


@profiled(key_args="input_size")
def process_data(input_size): ...


with Profiler() as prof:
    process_data(100)
    process_data(1000)

prof.summary()  # {"process_data(input_size=100)": ProfileStats(count=1, ...), ...}
```

## Data Comparison

`diff` lists every difference with its location; `equals` is its boolean form:

```python
from suthing import diff, equals

expected = {"a": {"b": 1, "c": [1, 2, 3]}}
actual = {"a": {"b": 1, "c": [1, 2]}}

equals(expected, actual)  # False
for d in diff(expected, actual):
    print(d)  # $.a.c[2]: missing item (expected=3, actual=<missing>)
```

## Next Steps

- Check out more [Examples](../examples.md)
- Read the complete [API Reference](../reference/index.md)
