package cli

import (
	"context"
	"fmt"
	"time"

	"github.com/spf13/cobra"

	"github.com/cie-team/cie/benchmark"
	"github.com/cie-team/cie/internal/backend"
	"github.com/cie-team/cie/internal/wandb"
)

func newWandBCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "wandb",
		Short: "Import metrics from a local Weights & Biases run directory",
	}
	sync := &cobra.Command{
		Use:   "sync [run-dir]",
		Short: "Ingest wandb-history.jsonl into trials (CIE_WANDB_RUN or ./wandb/latest-run if arg omitted)",
		Args:  cobra.MaximumNArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			var p string
			if len(args) > 0 {
				p = args[0]
			}
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()
			trials, err := b.IngestWandBRun(p)
			if err != nil {
				return err
			}
			abs, err := wandb.ResolveRunPath(p)
			if err != nil {
				return err
			}
			fmt.Fprintf(cmd.OutOrStdout(), "Imported %d trial(s) from %s\n", len(trials), abs)
			return nil
		},
	}
	cmd.AddCommand(sync)
	return cmd
}

func newBenchmarkCmd() *cobra.Command {
	var model string
	var executor string
	var traceDir string
	var caicBin string
	var caicArgs []string
	run := &cobra.Command{
		Use:   "run",
		Short: "Run the built-in benchmark harness (stub executor by default)",
		RunE: func(cmd *cobra.Command, args []string) error {
			tasks := benchmark.DefaultTasks()
			r := benchmark.NewRunner(model)
			ctx := context.Background()
			var execFn benchmark.Executor
			switch executor {
			case "stub", "":
				execFn = benchmark.StubExecutorContext()
			case "genai":
				cfg, err := LoadConfig(cmd)
				if err != nil {
					return err
				}
				cfg.ApplyEnvAPIKeys()
				td := traceDir
				if td == "" {
					td = benchmark.TraceDirFromEnv()
				}
				execFn = benchmark.GenAIExecutor(cfg, td)
			case "caic":
				execFn = benchmark.CaicExecutor(caicBin, caicArgs)
			default:
				return fmt.Errorf("unknown --executor %q (stub|genai|caic)", executor)
			}
			results, err := r.RunAll(ctx, tasks, execFn)
			if err != nil {
				return err
			}
			fmt.Fprintf(cmd.OutOrStdout(), "Benchmark run %s (%d tasks)\n", r.RunID, len(results))
			for _, res := range results {
				fmt.Fprintf(cmd.OutOrStdout(), "- %-26s %-10s success=%v dur=%s\n",
					res.Task.ID, res.Task.Difficulty, res.Metrics.Success,
					res.Metrics.Duration.Round(time.Millisecond))
			}
			fmt.Fprintf(cmd.OutOrStdout(), "Pass rate: %.0f%%\n", benchmark.PassRate(results)*100)
			if executor == "genai" && (traceDir != "" || benchmark.TraceDirFromEnv() != "") {
				fmt.Fprintln(cmd.OutOrStdout(),
					"Wrote minitrace prompts under the trace dir; inspect with go-minitrace validate / query duckdb.")
			}
			return nil
		},
	}
	run.Flags().StringVar(&model, "model", "go-harness", "model label for the run")
	run.Flags().StringVar(&executor, "executor", "stub", "task runner: stub (default), genai (maruel/genai + config), caic (subprocess + env)")
	run.Flags().StringVar(&traceDir, "trace-dir", "", "write minitrace sessions for genai runs (overrides CIE_TRACE_DIR)")
	run.Flags().StringVar(&caicBin, "caic-bin", "", "path to caic binary (default: CIE_CAIC_BIN or PATH)")
	run.Flags().StringSliceVar(&caicArgs, "caic-arg", nil, "extra arguments passed to caic (repeatable)")

	top := &cobra.Command{
		Use:   "benchmark",
		Short: "Agent-oriented benchmark harness (Go port)",
	}
	top.AddCommand(run)
	return top
}
