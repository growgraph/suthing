# Examples

Practical recipes for the utilities in Suthing.

## Configuration Files

```python
from suthing import FileHandle, load_env

config = FileHandle.load("config.yaml")
settings = FileHandle.load("settings.env")  # a dict; os.environ is untouched
load_env("settings.env")  # explicitly push into os.environ

FileHandle.dump(config, "config.json.gz")
```

## Large Record Files

Stream JSON Lines instead of loading them whole, and collect bad lines instead of failing:

```python
from suthing import iter_jsonl, read_jsonl, write_jsonl

for record in iter_jsonl("events.jsonl.gz"):
    handle(record)

rows, errors = read_jsonl("labels.jsonl", require_object=True)
for error in errors:
    print(error)  # "line 17: not valid JSON (...)"

write_jsonl(results, "out/results.jsonl", mkdir=True)
write_jsonl(more_results, "out/results.jsonl", append=True)
```

CSV files can be streamed in `DataFrame` chunks:

```python
from suthing import FileHandle

for chunk in FileHandle.iter("big.csv.gz", chunksize=50_000):
    process(chunk)
```

## Safe Checkpoints

A reader never sees a half-written file, and a crash mid-write leaves the previous checkpoint intact:

```python
from suthing import FileHandle, atomic_write

FileHandle.dump(state, "checkpoints/state.json")  # atomic by default
atomic_write("checkpoints/READY", "ok", durable=True)  # fsync before the rename
```

## Content Hashes and Cache Keys

```python
from suthing import file_hash, stable_hash, text_hash, tree_hash

key = stable_hash(
    {"model": "m", "params": {"k": 3}}, length=16
)  # key order does not matter
text_hash(prompt, length=12)
file_hash("data/corpus.tar")
tree_hash("data/corpus", pattern="*.json")
```

`stable_hash(obj)` equals `sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")))`, so it can replace that expression without changing hashes already stored.

## Performance

```python
from suthing import Profiler, Timer, profiled

with Timer() as t:
    result = process_large_dataset()
print(f"Dataset processing took {t.elapsed_str} ({t.elapsed_ms} ms)")


@profiled(key_args=["size", "batch_size"])
def process_data(size, batch_size):
    for i in range(0, size, batch_size):
        process_batch(i, batch_size)


with Profiler() as prof:
    process_data(size=1000, batch_size=100)
    process_data(size=1000, batch_size=50)

for key, stats in prof.summary().items():
    print(key, stats.count, stats.mean)
```

## Test Assertions

`diff` says where two structures differ, which makes failing assertions readable:

```python
from suthing import diff

differences = diff(expected, actual, rel_tol=1e-9, ignore_order=True)
assert not differences, "\n".join(map(str, differences))
```

## Small Helpers

```python
from suthing import batched, env_flag, setup_logging, slugify, to_jsonable, utc_now_iso

for batch in batched(rows, 500):
    db.insert_many(batch)

slugify("  Person / Company ")  # "Person-Company"
env_flag("MYAPP_DEBUG")  # "1"/"true"/"yes"/"on" → True; typos raise
setup_logging("INFO")  # or setup_logging(config="logging.conf")
to_jsonable({"when": datetime.now(), "score": numpy.float32(0.5)})
utc_now_iso()  # "2026-01-02T10:15:00+00:00"
```

## More Examples

- [API Reference](reference/index.md) - Complete API documentation
- [Quick Start](getting_started/quickstart.md) - Basic usage examples
