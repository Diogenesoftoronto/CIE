# CIE Technical Skills Documentation

This directory contains technical documentation for the CIE (Optimization & Evaluation) project.

## Available Documentation

### [Textual Framework Guide](textual.md)
Comprehensive guide to the Textual TUI framework patterns used in CIE. Covers:
- Core Textual concepts and widgets
- CIE-specific implementation patterns
- Panel architecture and message passing
- DataTable usage and styling
- Testing strategies for Textual applications

## Quick Reference

### Project Architecture
- **Single-file application**: All code in `main.py` (~650 lines)
- **Textual TUI framework**: Terminal-based user interface
- **Three-panel layout**: Optimizers | Evals | Experiments
- **Mock-first development**: Ready for real algorithm implementations

### Key Technologies
- **Python 3.13+**: Required version
- **Textual ≥0.47**: TUI framework (not 6.6.0+ as mentioned in some docs)
- **UV package manager**: Recommended for dependency management
- **Protocol-based design**: Extensible optimizer/evaluator interfaces

### Development Status
- ✅ Functional TUI application with mock algorithms
- ✅ Protocol-based architecture for easy extension
- ✅ Comprehensive documentation
- ⚠️ No test suite yet
- ⚠️ Mock implementations need replacement with real algorithms
- ⚠️ Single-file architecture may need modularization

## Getting Started

1. **Run the application**: `python main.py`
2. **Understand the UI**: Three panels for optimization, evaluation, and experiments
3. **Check the code**: All implementation details in `main.py`
4. **Review patterns**: See `textual.md` for Textual framework patterns used

## Next Steps

1. Add test infrastructure
2. Replace mock algorithms with real implementations  
3. Add persistence for trial history
4. Consider modularizing the single-file architecture