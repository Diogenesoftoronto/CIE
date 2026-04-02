# CIE Testing Guide

This guide outlines the testing infrastructure, categories, and best practices for the CIE project.

## Test Categories

The test suite is divided into several categories to ensure comprehensive coverage:

### 1. Backend Tests
- **Focus**: Core functionality of the `cie.core` module.
- **Key Tests**:
  - Backend initialization
  - Scoring logic (respecting metric weights)
  - State management (policy proposal and updates)
  - Statistics reporting

### 2. Benchmark Tests
- **Focus**: The `benchmark` package.
- **Key Tests**:
  - Task definitions and metadata
  - Metrics collection and calculation
  - Benchmark runner functionality
  - Integration testing

### 3. Context System Tests
- **Focus**: Context introspection and manipulation.
- **Key Tests**:
  - Context node creation and compression
  - Context introspection and manipulation
  - Agent context tools
  - Context-aware optimizers
  - Context evaluator
  - Protocol compliance

### 4. End-to-End Tests
- **Focus**: Complete workflows.
- **Key Tests**:
  - Full optimization cycles
  - Multiple optimizer usage
  - Pareto optimization
  - Policy adoption with guardrails
  - Storage persistence
  - Real model integration

### 5. Optimizer Tests
- **Focus**: Specific optimizer implementations.
- **Key Tests**:
  - DSPy optimizer behavior
  - Hill climb optimizer parameter ranges
  - Observer state updates

### 6. Type Checking Tests
- **Focus**: Static analysis and type safety.
- **Key Tests**:
  - Type annotations verification
  - Protocol compliance
  - Modal type checking
  - Backend type safety

## Test Infrastructure

### Mock Framework
- We use `unittest.mock` (`Mock`, `patch`) extensively to isolate units under test.
- External dependencies (tools, evaluators, introspectors) are mocked to ensure fast and reliable tests.

### Test Organization
- Tests are organized by class/module in the `tests/` directory.
- We use `pytest` fixtures for setup and teardown.
- Parametrization is used to test multiple scenarios efficiently.

### Running Tests

To run the full test suite:

```bash
pytest tests/
```

To run specific categories:

```bash
pytest tests/test_backend.py
pytest tests/test_benchmark.py
```

## Best Practices

1.  **Mock External Calls**: Avoid making real API calls or file system changes in unit tests.
2.  **Type Safety**: Ensure all new code is fully typed and passes type checking tests.
3.  **Coverage**: Aim for high coverage in core modules (`cie.core`, `cie.optimizers`).
4.  **Descriptive Names**: Use clear and descriptive names for test functions and classes.
