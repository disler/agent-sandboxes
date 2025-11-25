# Sandbox Common Library

Shared Python library for agent-sandboxes applications.

## Package

- **Name**: `sandbox-common`
- **Version**: 0.1.0

## Modules

- `src/config.py` - Configuration management
- `src/logging.py` - Logging utilities
- `src/sandbox.py` - E2B sandbox helpers
- `src/utils.py` - General utilities
- `src/errors.py` - Custom error classes

## Usage

To use this library in other apps within the monorepo:

```toml
# In your app's pyproject.toml
[project]
dependencies = [
    "sandbox-common",
]

[tool.uv.sources]
sandbox-common = { path = "../../lib", editable = true }
```

Then import in your Python code:

```python
from src.config import load_config
from src.logging import setup_logger
from src.sandbox import SandboxHelper
```

## Dependencies

- e2b>=2.6.4
- python-dotenv>=1.0.0
- rich>=13.0.0
