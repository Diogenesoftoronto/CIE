# CIE CLI Setup & Usage Guide

## Quick Start

### Installation

CIE is installed as a Python package with command-line entry points. To use the CLI commands:

```bash
# Install the package in development mode
cd /path/to/CIE
pip install -e .

# Or install with all optional dependencies
pip install -e ".[all]"
```

### Verify Installation

```bash
# Check if the CLI is available
cie --help

# Or run via Python module
python -m cie.cli --help
```

## Available Commands

### 1. Initialize Configuration

```bash
# Initialize CIE with default settings
cie init

# Initialize with specific model provider
cie init --model openai --model-name gpt-4o-mini

# Initialize with Kimi provider
cie init --model kimi --model-name kimi

# Use mock provider for testing
cie init --model mock

# Specify storage backend
cie init --storage sqlite
cie init --storage json
cie init --storage memory

# Custom experiments directory
cie init --experiments-dir /path/to/experiments
```

### 2. Run Optimization

```bash
# Run single optimization iteration
cie optimize

# Run multiple iterations
cie optimize --iterations 10

# Use specific optimizer (0-based index)
cie optimize --optimizer 0

# Use specific workload (0-based index)
cie optimize --workload 1

# Combine options
cie optimize --optimizer 0 --workload 0 --iterations 5 --save-policy

# Example: Run Hill Climb optimizer for 20 iterations
cie optimize --optimizer 1 --iterations 20
```

### 3. View Statistics

```bash
# Show current backend statistics
cie stats

# Output includes:
# - Total trials completed
# - Pareto frontier size
# - Available optimizers
# - Available workloads
# - Current active policy
# - Storage backend type
# - Best score achieved
# - Recent trials (last 7 days)
```

### 4. List Trials

```bash
# Show all trials with default sorting
cie trials

# Show trials sorted by score (best first)
cie trials --sort score

# Show Pareto frontier only
cie trials --pareto

# Show trials for specific optimizer
cie trials --optimizer 0

# Show trials for specific workload
cie trials --workload 0

# Limit number of trials displayed
cie trials --limit 10

# Show detailed metrics for each trial
cie trials --detail
```

### 5. View Pareto Frontier

```bash
# Show non-dominated solutions (Pareto frontier)
cie trials --pareto

# This shows the best trade-off solutions across all metrics
```

### 6. Adopt a Policy

```bash
# Adopt the best trial as active policy
cie adopt --best

# Adopt specific trial by ID
cie adopt --trial-id 42

# Adopt and specify name
cie adopt --best --name "my-optimized-policy"

# Save adopted policy to file
cie adopt --best --save-to policy.json
```

### 7. Manage Optimizers

```bash
# List available optimizers
cie optimizers

# Output shows:
# - Optimizer name and description
# - Best score achieved with this optimizer
# - Number of trials
# - Artifact ID if applicable

# Show optimizer details
cie optimizers --detail
```

### 8. Manage Evaluators

```bash
# List available evaluators
cie evaluators

# Output shows:
# - Evaluator name and slug
# - Description
# - Supported metrics
# - Tags (e.g., "fast", "accurate")

# Set default evaluator
cie evaluators --use mock

# Use specific evaluator
cie evaluators --use text-match

# Show evaluator capabilities
cie evaluators --detail
```

### 9. Start TUI Application

```bash
# Start the interactive Terminal User Interface
cie tui

# Or use the dedicated TUI command
cie-tui

# With debug output
cie --debug tui
```

### 10. Reset Backend

```bash
# Clear all trials and reset state
cie reset

# Warning: This will delete all experiment data!
# A confirmation prompt will appear.
```

### 11. Validate Configuration

```bash
# Validate a configuration file
cie validate-config /path/to/config.json

# Output shows:
# - Whether configuration is valid
# - Current settings (model, storage, etc.)
```

### 12. Show Configuration

```bash
# Display current configuration
cie config show

# Show specific setting
cie config show --key model.provider

# Update configuration
cie config set model.provider openai

# Save to file
cie config save /path/to/config.json
```

## Global Options

All commands accept these global options:

```bash
# Specify configuration file
cie --config /path/to/config.json COMMAND

# Enable debug mode
cie --debug COMMAND

# Show help for any command
cie COMMAND --help
```

## Configuration

### Configuration File Location

CIE looks for configuration in this order:

1. `--config` flag value (if specified)
2. `~/.cie/config.json` (user's home directory)
3. `.cie/config.json` (project directory)
4. Built-in defaults

### Configuration Structure

```json
{
  "model": {
    "provider": "kimi",
    "model_name": "kimi",
    "api_key": "your-api-key"
  },
  "storage": {
    "backend": "sqlite",
    "experiments_dir": "~/.cie/experiments"
  },
  "evaluation": {
    "default_evaluator": "mock",
    "metric_weights": {
      "latency_p95": 1.0,
      "cost_per_req": 1.0,
      "task_success": -2.0,
      "context_usage": 0.5
    }
  }
}
```

### Environment Variables

Set these to override configuration file settings:

```bash
# Model configuration
export CIE_MODEL_PROVIDER=openai
export CIE_MODEL_NAME=gpt-4o-mini
export CIE_API_KEY=sk-...

# Storage configuration
export CIE_STORAGE_BACKEND=sqlite
export CIE_EXPERIMENTS_DIR=/path/to/experiments

# Evaluation configuration
export CIE_DEFAULT_EVALUATOR=text-match
```

## Common Workflows

### Workflow 1: Quick Optimization

```bash
# 1. Initialize with default settings
cie init

# 2. Run optimization with 10 iterations
cie optimize --iterations 10

# 3. Check results
cie stats
cie trials --sort score

# 4. View Pareto frontier
cie trials --pareto

# 5. Adopt best policy
cie adopt --best
```

### Workflow 2: Compare Optimizers

```bash
# 1. Run with first optimizer (DSPy)
cie optimize --optimizer 0 --iterations 5

# 2. Run with second optimizer (Hill Climb)
cie optimize --optimizer 1 --iterations 5

# 3. Compare results
cie trials --detail
cie optimizers --detail
```

### Workflow 3: Different Workloads

```bash
# 1. Run on first workload
cie optimize --workload 0 --iterations 3

# 2. Run on second workload
cie optimize --workload 1 --iterations 3

# 3. Run on third workload
cie optimize --workload 2 --iterations 3

# 4. Review all results
cie trials --detail
```

### Workflow 4: Using Different Models

```bash
# 1. Initialize with OpenAI
cie init --model openai --model-name gpt-4o-mini
export OPENAI_API_KEY=sk-...

# 2. Run optimization
cie optimize --iterations 5

# 3. Switch to Kimi
cie init --model kimi --model-name kimi
export KIMI_API_KEY=...

# 4. Run with different model
cie optimize --iterations 5

# 5. Compare results
cie trials --detail
```

## Troubleshooting

### Command Not Found

**Problem**: `cie: command not found`

**Solution**:
```bash
# Make sure package is installed in editable mode
pip install -e .

# Or try running via Python module
python -m cie.cli --help

# Check installation
python -c "from cie.cli import main; print('✅ CLI installed')"
```

### Configuration Issues

**Problem**: "Configuration file not found"

**Solution**:
```bash
# Initialize configuration
cie init

# Or specify config file explicitly
cie --config /path/to/config.json stats

# Check config location
ls -la ~/.cie/config.json
```

### API Key Not Found

**Problem**: "API key not configured"

**Solution**:
```bash
# Option 1: Set environment variable
export OPENAI_API_KEY=sk-...
export KIMI_API_KEY=...

# Option 2: Initialize with API key
cie init --model openai --api-key sk-...

# Option 3: Edit configuration file
nano ~/.cie/config.json  # Add api_key field
```

### No Trials Found

**Problem**: `cie trials` shows no results

**Solution**:
```bash
# Run an optimization first
cie optimize

# Then check trials
cie trials

# Check statistics
cie stats
```

### Model Provider Issues

**Problem**: "Model provider not available"

**Solution**:
```bash
# Use mock provider for testing
cie init --model mock

# Check available providers
python -c "from cie.utils.model_providers import PROVIDERS; print(PROVIDERS.keys())"

# Install required dependencies
pip install ".[ai]"  # For AI models
```

## Output Examples

### `cie stats`

```
Backend Statistics:
------------------------------
Trials: 42
Pareto frontier: 8
Optimizers: 2
Workloads: 5
Active policy: my-optimized-policy
Storage: sqlite
Best score: -0.89
Recent trials (7 days): 12
```

### `cie trials --limit 3`

```
ID  Policy Name              Score   Latency  Success  Workload
--- ----------------------- ------- --------- ------- -----------
1   DSPy:BootstrapFewShot#1 -0.925  145.2ms   0.95    MicroEval:basic
2   DSPy:BootstrapFewShot#2 -0.812  198.5ms   0.87    MicroEval:advanced
3   HillClimb#1             -0.756  167.8ms   0.91    MicroEval:stress
```

### `cie optimizers --detail`

```
Optimizer: DSPy:BootstrapFewShot
  Description: DSPy-based optimizer with bootstrap few-shot learning
  Best Score: -0.925
  Trials: 23
  Artifact: /path/to/artifacts/dspy_v1.pkl

Optimizer: HillClimbOptimizer
  Description: Hill climbing with adaptive step sizes
  Best Score: -0.756
  Trials: 19
  Artifact: None
```

### `cie evaluators --detail`

```
Evaluator: mock
  Description: Mock evaluator with realistic behavior
  Slug: mock
  Metrics: latency_p95, cost_per_req, task_success, tool_error_rate
  Tags: [fast, development, testing]

Evaluator: text-match
  Description: Text matching evaluator with Levenshtein/Jaccard metrics
  Slug: text-match
  Metrics: text_exact_match, text_levenshtein, text_jaccard
  Tags: [accurate, nlp, evaluation]
```

## Advanced Usage

### Scripting with CLI

```bash
#!/bin/bash

# Run multiple optimization experiments
for i in {1..5}; do
    echo "Experiment $i:"
    cie optimize --iterations 10 --optimizer 0
    cie stats
    echo "---"
done

# Export results
cie trials --detail > results.txt
cie trials --pareto > pareto.txt
```

### Integration with Other Tools

```bash
# Get best score as JSON
cie stats --format json | jq '.best_score'

# Count trials by optimizer
cie trials --detail --format json | jq 'group_by(.policy_name) | map({optimizer: .[0].policy_name, count: length})'

# Find Pareto frontier trials
cie trials --pareto --format json | jq '.[] | select(.pareto == true)'
```

### Batch Processing

```bash
# Run optimization on all workloads
for workload in {0..4}; do
    cie optimize --workload $workload --iterations 5
done

# Aggregate results
cie trials --detail
```

## Tips & Best Practices

1. **Use Mock Provider for Testing**: Start with `--model mock` to test workflows without API calls

2. **Save Configurations**: Create named configurations for different scenarios
   ```bash
   cp ~/.cie/config.json ~/.cie/config.openai.json
   cie --config ~/.cie/config.openai.json stats
   ```

3. **Monitor Progress**: Run `cie stats` periodically to track optimization progress

4. **Review Pareto Frontier**: Use `cie trials --pareto` to identify best trade-off solutions

5. **Keep API Keys Secure**: Use environment variables instead of hardcoding in config files

6. **Clean Up Regularly**: Use `cie reset` to clear old experiments when needed

7. **Export Results**: Save results to files for analysis
   ```bash
   cie trials --detail > results.txt
   ```

8. **Debug Issues**: Use `cie --debug COMMAND` for detailed error messages

## Further Resources

- See `README.md` for project overview
- See `AGENTS.md` for architecture and patterns
- See `TEST_IMPROVEMENTS_SUMMARY.md` for testing information
- Run `cie COMMAND --help` for command-specific help