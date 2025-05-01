# Installation

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

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

## Development Installation

If you want to contribute to Suthing or run the tests:

1. Clone the repository:
```bash
git clone https://github.com/growgraph/suthing.git
cd suthing
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

## Troubleshooting

If you encounter any issues during installation:

1. Make sure you have Python 3.10 or higher installed
2. Try upgrading pip: `pip install --upgrade pip`
3. Check if all dependencies are properly installed
4. If problems persist, please open an issue on GitHub 