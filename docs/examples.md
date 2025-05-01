# Examples

This page contains practical examples of using Suthing in real-world scenarios.

## Configuration Management

Load and manage configuration files with automatic format detection:

```python
from suthing import FileHandle

# Load configuration from different formats
config = FileHandle.load("config.yaml")
env_vars = FileHandle.load(".env")
df = FileHandle.load("secrets.csv")

# Save configuration with compression
FileHandle.dump(config, "config.json.gz")
```

## Performance Optimization

Identify bottlenecks in your code:

```python
from suthing import Timer, profile, SProfiler

# Time a specific operation
with Timer() as t:
    result = process_large_dataset()
print(f"Dataset processing took {t.elapsed_str}")

# Profile a function with different inputs
profiler = SProfiler()

@profile(_argnames=["size", "batch_size"])
def process_data(size, batch_size):
    for i in range(0, size, batch_size):
        process_batch(i, batch_size)

# Run with different parameters
process_data(size=1000, batch_size=100, _profiler=profiler)
process_data(size=1000, batch_size=50, _profiler=profiler)

# Compare performance
stats = profiler.view_stats()
```

## Database Connection Management

Create and manage database connections with automatic type detection:

```python
from suthing.connection import ConfigFactory

# ArangoDB connection
arango_config = ConfigFactory.create_config("http://localhost:8529")

# Neo4j connection
neo4j_config = ConfigFactory.create_config({
    "port": "7474",
    "username": "neo4j",
    "password": "password"
})

# WSGI application
wsgi_config = ConfigFactory.create_config({
    "port": "8000",
    "host": "0.0.0.0",
    "path": "/api"
})
```

## Data Validation

Compare and validate complex data structures:

```python
from suthing import equals

# Compare configuration files
config1 = FileHandle.load("config1.yaml")
config2 = FileHandle.load("config2.yaml")
if not equals(config1, config2):
    print("Configurations differ!")

# Compare nested data structures
expected = {
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "settings": {"theme": "dark", "notifications": True}
}

actual = {
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "settings": {"theme": "dark", "notifications": True}
}

if equals(expected, actual):
    print("Data matches expected structure")
```

## Error Handling

Use decorators for secure function execution:

```python
from suthing import secure_execution

@secure_execution
def process_sensitive_data(data):
    # Your code here
    return result

# The function will handle errors gracefully
result = process_sensitive_data(data)
```

## More Examples

For more detailed examples and use cases, check out:

<!-- - [Features](features/) - Detailed documentation of all features -->
- [API Reference](reference/index.md) - Complete API documentation
- [Quick Start](getting_started/quickstart.md) - Basic usage examples
