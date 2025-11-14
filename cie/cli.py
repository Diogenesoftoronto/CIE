"""
Command-line interface for CIE.
"""

import json
import sys
import time
from pathlib import Path

import click

from cie.config.settings import CIEConfig, get_config, set_config
from cie.core.backend import CIEBackend
from cie.evaluators import list_evaluators


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def cli(ctx, config: str | None, debug: bool):
    """CIE (Optimization & Evaluation) - AI-powered optimization framework."""
    ctx.ensure_object(dict)
    # Load configuration
    if config:
        config_obj = CIEConfig(config_file=config)
    else:
        config_obj = get_config()
    if debug:
        config_obj.debug = True
        config_obj.log_level = "DEBUG"
    set_config(config_obj)
    ctx.obj["config"] = config_obj


@cli.command()
@click.option("--model", "-m", default="kimi", help="Model provider (openai, kimi, mock)")
@click.option("--model-name", default="kimi", help="Specific model name")
@click.option("--api-key", help="API key for model provider")
@click.option("--storage", default="json", help="Storage backend (sqlite, json, memory)")
@click.option("--experiments-dir", default="~/.cie/experiments", help="Experiments directory")
@click.pass_context
def init(ctx, model: str, model_name: str, api_key: str, storage: str, experiments_dir: str):
    """Initialize CIE configuration."""
    config = ctx.obj["config"]
    # Update configuration
    config.model.provider = model
    config.model.model_name = model_name
    if api_key:
        config.model.api_key = api_key
    config.storage.backend = storage
    config.storage.experiments_dir = experiments_dir
    # Create directories
    experiments_path = Path(experiments_dir).expanduser()
    experiments_path.mkdir(parents=True, exist_ok=True)
    # Save configuration
    config_file = Path.home() / ".cie" / "config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config.save_to_file(str(config_file))
    click.echo("CIE initialized with:")
    click.echo(f"  Model: {model} ({model_name})")
    click.echo(f"  Storage: {storage}")
    click.echo(f"  Config: {config_file}")
    click.echo(f"  Experiments: {experiments_path}")


@cli.command()
@click.option("--optimizer", "-o", default=0, help="Optimizer index to use")
@click.option("--workload", "-w", default=0, help="Workload index to use")
@click.option("--iterations", "-i", default=1, help="Number of iterations")
@click.option("--save-policy", is_flag=True, help="Save the best policy")
@click.pass_context
def optimize(ctx, optimizer: int, workload: int, iterations: int, save_policy: bool):
    """Run optimization experiment."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        click.echo(f"Starting optimization with {iterations} iterations...")
        click.echo(f"Optimizer: {optimizer}")
        click.echo(f"Workload: {workload}")
        best_trial = None
        best_score = float("inf")
        for i in range(iterations):
            # Generate policy
            policy = backend.propose_once(optimizer)
            # Evaluate policy
            trial = backend.eval_policy(policy, workload)
            # Track best trial
            if trial.score < best_score:
                best_score = trial.score
                best_trial = trial
            # Progress indicator
            if (i + 1) % 10 == 0 or i == 0:
                click.echo(f"  Iteration {i + 1}/{iterations}: score={trial.score:.4f}")
        # Show results
        click.echo("\nOptimization complete!")
        click.echo(f"Best score: {best_score:.4f}")
        if best_trial:
            click.echo(f"Best trial: #{best_trial.id}")
            click.echo(f"Policy: {best_trial.policy_name}")
            click.echo("Metrics:")
            for metric, value in best_trial.metrics.items():
                click.echo(f"  {metric}: {value}")
            # Save policy if requested
            if save_policy:
                policy_file = (
                    Path(config.storage.experiments_dir) / f"best_policy_{int(time.time())}.json"
                )
                with open(policy_file, "w") as f:
                    json.dump(
                        {
                            "trial_id": best_trial.id,
                            "policy_name": best_trial.policy_name,
                            "score": best_trial.score,
                            "metrics": best_trial.metrics,
                            "params": best_trial.metadata.get("policy_params", {}),
                        },
                        f,
                        indent=2,
                    )
                click.echo(f"Best policy saved to: {policy_file}")
        backend.close()
    except Exception as e:
        click.echo(f"Error during optimization: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--trial-id", type=int, help="Specific trial ID to show")
@click.option("--limit", "-l", default=20, help="Number of recent trials to show")
@click.option("--pareto", is_flag=True, help="Show Pareto frontier")
@click.pass_context
def trials(ctx, trial_id: int | None, limit: int, pareto: bool):
    """Show trial history."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        if trial_id is not None:
            # Show specific trial
            trial = next((t for t in backend.trials if t.id == trial_id), None)
            if trial:
                click.echo(f"Trial #{trial.id}:")
                click.echo(f"  Policy: {trial.policy_name}")
                click.echo(f"  Workload: {trial.workload}")
                click.echo(f"  Score: {trial.score:.4f}")
                click.echo(f"  Created: {trial.created_at}")
                click.echo("  Metrics:")
                for metric, value in trial.metrics.items():
                    click.echo(f"    {metric}: {value}")
            else:
                click.echo(f"Trial #{trial_id} not found", err=True)
        else:
            # Show recent trials
            recent_trials = backend.trials[-limit:]
            if pareto:
                click.echo("Pareto Frontier:")
                trials_to_show = backend.pareto
            else:
                click.echo(f"Recent Trials (last {len(recent_trials)}):")
                trials_to_show = recent_trials
            if trials_to_show:
                # Header
                click.echo(
                    f"{'ID':>4} {'Policy':<20} {'Score':<8} {'Latency':<8} {'Cost':<8} {'Success':<8}"
                )
                click.echo("-" * 70)
                # Trials
                for trial in trials_to_show:
                    click.echo(
                        f"{trial.id:>4} "
                        f"{trial.policy_name:<20.20} "
                        f"{trial.score:<8.4f} "
                        f"{trial.metrics.get('latency_p95', 0):<8.1f} "
                        f"{trial.metrics.get('cost_per_req', 0):<8.5f} "
                        f"{trial.metrics.get('task_success', 0):<8.3f}"
                    )
            else:
                click.echo("No trials found")
        backend.close()
    except Exception as e:
        click.echo(f"Error showing trials: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def optimizers(ctx):
    """List available optimizers."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        optimizers = backend.list_optimizers()
        click.echo("Available Optimizers:")
        click.echo("-" * 50)
        for i, (name, meta) in enumerate(optimizers):
            click.echo(f"{i}: {name}")
            for key, value in meta.items():
                if value is not None:
                    click.echo(f"   {key}: {value}")
            click.echo()
        backend.close()
    except Exception as e:
        click.echo(f"Error listing optimizers: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--use", "use_slug", help="Set default evaluator (e.g., mock, text-match)")
@click.pass_context
def evaluators(ctx, use_slug: str | None):
    """List or update available evaluators."""
    try:
        registrations = list_evaluators()
        click.echo("Available Evaluators:")
        click.echo("-" * 50)
        for reg in registrations:
            tags = f" ({', '.join(reg.tags)})" if reg.tags else ""
            click.echo(f"{reg.name}{tags}")
            if reg.description:
                click.echo(f"   {reg.description}")
        if use_slug:
            ctx.obj["config"].evaluation.default_evaluator = use_slug
            config_file = Path.home() / ".cie" / "config.json"
            ctx.obj["config"].save_to_file(str(config_file))
            click.echo(f"\nDefault evaluator updated to '{use_slug}' and saved to {config_file}")
    except Exception as e:
        click.echo(f"Error handling evaluators: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def workloads(ctx):
    """List available workloads."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        click.echo("Available Workloads:")
        click.echo("-" * 50)
        for i, workload in enumerate(backend.workloads):
            click.echo(f"{i}: {workload.name}")
            click.echo(f"   Items: {workload.items}")
            if workload.description:
                click.echo(f"   Description: {workload.description}")
            click.echo()
        backend.close()
    except Exception as e:
        click.echo(f"Error listing workloads: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--trial-id", type=int, required=True, help="Trial ID to adopt")
@click.pass_context
def adopt(ctx, trial_id: int):
    """Adopt a policy from a trial."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        result = backend.adopt_policy(trial_id)
        if result:
            click.echo(f"Successfully adopted trial #{trial_id}")
            if backend.active_policy:
                click.echo(f"Active policy: {backend.active_policy.name}")
                click.echo("Actions:")
                for action in backend.active_policy.actions:
                    click.echo(f"  - {action}")
        else:
            click.echo(f"Failed to adopt trial #{trial_id}", err=True)
            click.echo("Possible reasons:")
            click.echo("  - Trial not found")
            click.echo("  - Trial failed guardrails (high error rate, low success rate, etc.)")
        backend.close()
    except Exception as e:
        click.echo(f"Error adopting policy: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx):
    """Show backend statistics."""
    config = ctx.obj["config"]
    try:
        backend = CIEBackend(config)
        stats = backend.get_stats()
        click.echo("Backend Statistics:")
        click.echo("-" * 30)
        click.echo(f"Trials: {stats['trial_count']}")
        click.echo(f"Pareto frontier: {stats['pareto_count']}")
        click.echo(f"Optimizers: {stats['optimizer_count']}")
        click.echo(f"Workloads: {stats['workload_count']}")
        click.echo(f"Active policy: {'Yes' if stats['active_policy'] else 'No'}")
        click.echo(f"Storage: {stats['storage_type']}")
        if stats["best_score"] is not None:
            click.echo(f"Best score: {stats['best_score']:.4f}")
        click.echo(f"Recent trials (7 days): {stats['recent_trials']}")
        backend.close()
    except Exception as e:
        click.echo(f"Error getting stats: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def reset(ctx):
    """Reset backend (clear all trials and policies)."""
    config = ctx.obj["config"]
    if not click.confirm("This will clear all trials and policies. Are you sure?"):
        click.echo("Reset cancelled")
        return
    try:
        backend = CIEBackend(config)
        trial_count = len(backend.trials)
        backend.reset()
        click.echo(f"Backend reset complete. Cleared {trial_count} trials.")
        backend.close()
    except Exception as e:
        click.echo(f"Error resetting backend: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8080, help="Port to bind to")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def serve(ctx, host: str, port: int, debug: bool):
    """Start web server (placeholder)."""
    click.echo("Web server not implemented yet.")
    click.echo(f"Would start server at {host}:{port}")


@cli.command()
@click.pass_context
def tui(ctx):
    """Start the TUI application."""
    config = ctx.obj["config"]
    try:
        from cie.ui.app import main

        main(config)
    except ImportError:
        click.echo("TUI not available. Install with: pip install cie[ui]", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error starting TUI: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("config_file", type=click.Path())
@click.pass_context
def validate_config(ctx, config_file: str):
    """Validate configuration file."""
    try:
        config = CIEConfig(config_file=config_file)
        click.echo(f"Configuration file '{config_file}' is valid")
        # Show configuration summary
        click.echo("\nConfiguration summary:")
        click.echo(f"  Model provider: {config.model.provider}")
        click.echo(f"  Model name: {config.model.model_name}")
        click.echo(f"  Storage backend: {config.storage.backend}")
        click.echo(f"  Experiments directory: {config.storage.experiments_dir}")
    except Exception as e:
        click.echo(f"Configuration file '{config_file}' is invalid: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CIE CLI."""
    cli()


if __name__ == "__main__":
    main()
