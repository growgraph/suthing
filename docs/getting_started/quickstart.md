# Quick Start

This guide will help you get started with Suthing quickly. We'll cover the main features with simple examples.

## File Handling

Suthing makes file operations simple with automatic format detection:

```python
from suthing import FileHandle

# Read a YAML file
data = FileHandle.load("config.yaml")

# Write to a compressed JSON file
FileHandle.dump(data, "output.json.gz")
```

## Performance Measurement

Time your code execution easily:

```python
from suthing import Timer

with Timer() as t:
    # Your code here
    result = some_expensive_operation()
print(f"Operation took {t.elapsed_str}")
```

## Profiling Functions

Profile your functions to understand their performance:

```python
from suthing import profile, SProfiler

profiler = SProfiler()

@profile(_argnames="input_size")
def process_data(input_size):
    # Process data based on input size
    return result

# Run with profiler
result = process_data(input_size=100, _profiler=profiler)

# View profiling results
stats = profiler.view_stats()
```

## Data Comparison

Compare complex data structures:

```python
from suthing import equals

# Compare nested dictionaries
dict1 = {"a": {"b": 1, "c": [1, 2, 3]}}
dict2 = {"a": {"b": 1, "c": [1, 2, 3]}}
result = equals(dict1, dict2)  # True
```

## Connection Management

Create and manage database connections:

```python
from suthing.connection import ConfigFactory

# Create a connection from URL
config = ConfigFactory.create_config(url="http://localhost:8529")
# This will automatically detect it's an ArangoDB connection based on port

# Or from a dictionary
config = ConfigFactory.create_config(dict_like={
    "port": "8529",
    "username": "user",
    "password": "pass"
})
```

## Next Steps

<!-- - Explore the [Features](features/) section for detailed documentation -->
- Check out more [Examples](../examples.md)
- Read the complete [API Reference](../reference/index.md) 