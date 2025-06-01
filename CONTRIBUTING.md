# Contributing to VirtualPackaging

First off, thank you for considering contributing to VirtualPackaging! It's people like you that make VirtualPackaging such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for VirtualPackaging. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**

* Check the documentation for tips on solving your issue.
* Check if the bug has already been reported in the Issues section.
* Ensure the bug is related to the VirtualPackaging code and not a dependency.

**How Do I Submit A Good Bug Report?**

Bugs are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title.
* Describe the exact steps which reproduce the problem.
* Provide specific examples to demonstrate the steps.
* Describe the behavior you observed after following the steps.
* Explain which behavior you expected to see instead and why.
* Include screenshots or animated GIFs if possible.
* Include details about your configuration and environment.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for VirtualPackaging, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion:**

* Check if the enhancement has already been suggested in the Issues section.
* Check if the enhancement is already available in the latest version.

**How Do I Submit A Good Enhancement Suggestion?**

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title.
* Provide a detailed description of the suggested enhancement.
* Explain why this enhancement would be useful to most VirtualPackaging users.
* List some other applications where this enhancement exists, if applicable.
* Specify which version of VirtualPackaging you're using.
* Specify the name and version of the OS you're using.

### Pull Requests

The process described here has several goals:

* Maintain VirtualPackaging's quality
* Fix problems that are important to users
* Engage the community in working toward the best possible VirtualPackaging
* Enable a sustainable system for VirtualPackaging's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Fork the repository
2. Create a new branch for each feature or improvement
3. Send a pull request from each feature branch to the **main** branch

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* When only changing documentation, include [ci skip] in the commit title

### Python Styleguide

* Follow PEP 8 for Python code
* Use docstrings for all functions, classes, and modules
* Write tests for all new code

### JavaScript Styleguide

* Use ES6 syntax when possible
* Use semicolons at the end of each statement
* Prefer const over let over var
* Place imports in the following order:
  * External imports (e.g., from node_modules)
  * Internal imports (your own components/functions)
* Use meaningful variable names

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs
* `enhancement` - Issues that are feature requests
* `documentation` - Issues or pull requests related to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

Thank you for contributing to VirtualPackaging!

## Running Tests

This project uses pytest for testing. Ensure you have it installed (it's included in `requirements.txt`).

To run all tests, navigate to the root directory of the project and run:

```bash
pytest
```

To run tests for a specific file:

```bash
pytest tests/core/design/test_box_generator.py
```

To run a specific test function:

```bash
pytest tests/core/design/test_box_generator.py::test_add_padding
```

Please ensure all tests pass before submitting a pull request. Add new tests for any new features or bug fixes.

### Code Formatting and Linting (Python)

We use **Black** for uncompromising Python code formatting and **Flake8** for linting to ensure code quality and consistency.

**Configuration:**
*   Black is configured in `pyproject.toml`.
*   Flake8 uses default settings but can be configured in `.flake8` if needed.

**Usage:**

Before committing your Python changes, please format and lint your code:

1.  **Format with Black:**
    ```bash
    black .
    ```

2.  **Lint with Flake8:**
    ```bash
    flake8 .
    ```

It's highly recommended to integrate these tools into your code editor for automatic formatting and linting on save.
