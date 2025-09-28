Development
===========

Contributing to GIF-Tools
-------------------------

We welcome contributions! Please follow these guidelines:

Getting Started
~~~~~~~~~~~~~~~

1. Fork the repository
2. Clone your fork: ``git clone https://github.com/yourusername/GIF-Tools.git``
3. Create a feature branch: ``git checkout -b feature-name``
4. Install development dependencies: ``pip install -r requirements/dev.txt``
5. Make your changes
6. Run tests: ``pytest``
7. Run linting: ``flake8 gif_tools tests``
8. Commit your changes: ``git commit -m "feat: add new feature"``
9. Push to your fork: ``git push origin feature-name``
10. Create a Pull Request

Code Style
----------

We use the following tools to maintain code quality:

* **Black** for code formatting
* **Flake8** for linting
* **MyPy** for type checking
* **Pre-commit** hooks for automated checks

Run all checks:
.. code-block:: bash

   pre-commit run --all-files

Testing
-------

Run all tests:
.. code-block:: bash

   pytest

Run with coverage:
.. code-block:: bash

   pytest --cov=gif_tools --cov-report=html

Run specific test categories:
.. code-block:: bash

   pytest tests/unit/          # Unit tests
   pytest tests/integration/   # Integration tests
   pytest tests/performance/   # Performance tests

Documentation
-------------

Build documentation:
.. code-block:: bash

   cd docs
   sphinx-build -b html source build

View documentation:
.. code-block:: bash

   open docs/build/index.html  # macOS
   start docs/build/index.html  # Windows
   xdg-open docs/build/index.html  # Linux

Project Structure
-----------------

::

   GIF-Tools/
   ├── gif_tools/              # Core library
   │   ├── core/               # 17 GIF processing tools
   │   ├── utils/              # Utility modules
   │   └── __init__.py
   ├── desktop_app/            # Desktop GUI application
   ├── web_api/                # Future web API
   ├── tests/                  # Test suite
   │   ├── unit/               # Unit tests
   │   ├── integration/        # Integration tests
   │   └── performance/        # Performance tests
   ├── docs/                   # Documentation
   ├── requirements/           # Dependency files
   └── .github/workflows/      # CI/CD pipelines

Release Process
---------------

1. Update version in ``pyproject.toml``
2. Update ``CHANGELOG.md``
3. Create a release tag: ``git tag v1.0.0``
4. Push tag: ``git push origin v1.0.0``
5. GitHub Actions will automatically build and publish to PyPI
