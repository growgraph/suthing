# Installation

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (for development) or pip (for end-user install)

## Installation Steps

1. Install Suthing using pip:

```bash
pip install suthing
```

2. Verify the installation:

```python
import suthing

print(suthing.__version__)
```

## Dependencies

Suthing requires the following packages:

- pandas
- PyYAML
- python-dotenv

These will be automatically installed when you install Suthing using pip.

Reading and writing `.zst` (Zstandard) files needs one optional package:

```bash
pip install "suthing[zstd]"
```

## Development Installation

If you want to contribute to Suthing or run the tests:

1. Clone the repository:
```bash
git clone https://github.com/growgraph/suthing.git
cd suthing
```

2. Install development dependencies (uses `[dependency-groups]`, not optional extras):
```bash
uv sync --group dev
```

3. Install pre-commit hooks:
```bash
uv run pre-commit install
```

4. Run tests and type checks:
```bash
uv run pytest test
uv run ty check suthing test
```

## Troubleshooting

If you encounter any issues during installation:

1. Make sure you have Python 3.11 or higher installed
2. For pip installs, try upgrading pip: `pip install --upgrade pip`
3. Check if all dependencies are properly installed
4. If problems persist, please open an issue on GitHub
