### Project Guidelines - state-flow

This document outlines the coding standards and development practices for the `state-flow` project.

#### 1. General Principles
- **Clarity and Simplicity**: Write code that is easy to read and understand.
- **Consistency**: Maintain a consistent coding style across the project.
- **Type Safety**: Use Python type hints for all function signatures and variable declarations to improve maintainability and catch errors early.

#### 2. Python Coding Standards
- **Python Version**: The project targets Python 3.10 or higher.
- **Style Guide**: Follow PEP 8 guidelines for Python code.
- **Type Hinting**: Mandatory for all new code. Use `typing` module where necessary.
- **Docstrings**: Use Google-style docstrings for all public modules, classes, and functions.

#### 3. Data Validation and Modeling (Pydantic)
- This project uses **Pydantic v2** (specifically the latest available version) for data validation and settings management.
- Prefer `BaseModel` for data structures.
- Use `Field` to provide extra metadata and validation rules.
- Leverage Pydantic's type coercion and validation features instead of manual checks.

#### 4. Dependency Management (uv)
- Use `uv` for managing dependencies and virtual environments.
- To add a new dependency: `uv add <package_name>`
- To sync dependencies: `uv sync`
- Do not manually edit `pyproject.toml` dependencies unless necessary; use the `uv` CLI.

#### 5. Project Structure and Naming
- Follow standard Python naming conventions:
    - Classes: `PascalCase`
    - Functions/Variables: `snake_case`
    - Constants: `UPPER_SNAKE_CASE`
- Maintain a clean directory structure. Source code should be organized logically within the project root or a dedicated `src/` or package directory.

#### 6. Version Control
- Commit messages should be clear and descriptive.
- Use feature branches for new developments and merge via Pull Requests (or Merge Requests).
