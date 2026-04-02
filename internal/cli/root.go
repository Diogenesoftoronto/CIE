package cli

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/spf13/cobra"

	"github.com/cie-team/cie/internal/backend"
	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
	"github.com/cie-team/cie/internal/evaluator"
)

// NewRoot returns the full Cobra tree (Go-only CIE).
func NewRoot() *cobra.Command {
	root := &cobra.Command{
		Use:     "cie",
		Short:   "CIE — optimization & evaluation",
		Version: Version,
		Long: "CIE runs optimization experiments and multi-metric evaluation.\n" +
			"CLI and TUI use Charmbracelet (Bubble Tea, Lip Gloss) and Cobra.",
	}

	root.PersistentFlags().StringP("config", "c", "", "configuration file path")
	root.PersistentFlags().Bool("debug", false, "enable debug logging")

	root.AddCommand(newInitCmd())
	root.AddCommand(newOptimizeCmd())
	root.AddCommand(newTrialsCmd())
	root.AddCommand(newOptimizersCmd())
	root.AddCommand(newEvaluatorsCmd())
	root.AddCommand(newWorkloadsCmd())
	root.AddCommand(newAdoptCmd())
	root.AddCommand(newStatsCmd())
	root.AddCommand(newResetCmd())
	root.AddCommand(newServeCmd())
	root.AddCommand(newValidateConfigCmd())
	root.AddCommand(newTUICmd())
	root.AddCommand(newDoctorCmd())
	root.AddCommand(newWandBCmd())
	root.AddCommand(newBenchmarkCmd())

	return root
}

func newInitCmd() *cobra.Command {
	var model, modelName, storage, experiments, apiKey string

	cmd := &cobra.Command{
		Use:   "init",
		Short: "Initialize CIE configuration under ~/.cie/",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg := config.Default()
			cfg.Model.Provider = model
			cfg.Model.ModelName = modelName
			if apiKey != "" {
				cfg.Model.APIKey = apiKey
			}
			cfg.Storage.Backend = storage
			cfg.Storage.ExperimentsDir = experiments
			cfg.ExpandPaths()
			if err := os.MkdirAll(cfg.Storage.ExperimentsDir, 0o755); err != nil {
				return err
			}
			path, err := config.DefaultConfigPath()
			if err != nil {
				return err
			}
			if err := cfg.Save(path); err != nil {
				return err
			}
			fmt.Fprintln(cmd.OutOrStdout(), "CIE initialized")
			fmt.Fprintf(cmd.OutOrStdout(), "  Config: %s\n", path)
			fmt.Fprintf(cmd.OutOrStdout(), "  Storage: %s\n", cfg.Storage.Backend)
			fmt.Fprintf(cmd.OutOrStdout(), "  Experiments dir: %s\n", cfg.Storage.ExperimentsDir)
			return nil
		},
	}
	cmd.Flags().StringVarP(&model, "model", "m", "mock", "model provider label")
	cmd.Flags().StringVar(&modelName, "model-name", "mock", "model name")
	cmd.Flags().StringVar(&apiKey, "api-key", "", "API key for provider")
	cmd.Flags().StringVar(&storage, "storage", "json", "storage backend (json, sqlite, memory)")
	cmd.Flags().StringVar(&experiments, "experiments-dir", "~/.cie/experiments", "experiments directory")
	return cmd
}

func newOptimizeCmd() *cobra.Command {
	var optIdx, wlIdx, iterations int
	var savePolicy bool

	cmd := &cobra.Command{
		Use:   "optimize",
		Short: "Run optimization iterations (propose + eval)",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()

			fmt.Fprintf(cmd.OutOrStdout(), "Starting %d iterations (optimizer=%d workload=%d)…\n",
				iterations, optIdx, wlIdx)

			bestScore := 1e9
			var bestID int
			for i := 0; i < iterations; i++ {
				pol, err := b.ProposeOnce(optIdx)
				if err != nil {
					return err
				}
				tr, err := b.EvalPolicy(pol, wlIdx)
				if err != nil {
					return err
				}
				if i == 0 || tr.Score < bestScore {
					bestScore = tr.Score
					bestID = tr.ID
				}
				if (i+1)%10 == 0 || i == 0 {
					fmt.Fprintf(cmd.OutOrStdout(), "  iteration %d/%d: score=%.4f\n", i+1, iterations, tr.Score)
				}
			}
			fmt.Fprintln(cmd.OutOrStdout(), "Optimization complete")
			fmt.Fprintf(cmd.OutOrStdout(), "Best score: %.4f (trial #%d)\n", bestScore, bestID)
			if savePolicy {
				path := fmt.Sprintf("%s/best_policy_%d.json", cfg.Storage.ExperimentsDir, bestID)
				payload := map[string]any{"trial_id": bestID, "score": bestScore}
				raw, _ := json.MarshalIndent(payload, "", "  ")
				if err := os.WriteFile(path, raw, 0o644); err != nil {
					return err
				}
				fmt.Fprintf(cmd.OutOrStdout(), "Wrote %s\n", path)
			}
			return nil
		},
	}
	cmd.Flags().IntVarP(&optIdx, "optimizer", "o", 0, "optimizer index")
	cmd.Flags().IntVarP(&wlIdx, "workload", "w", 0, "workload index")
	cmd.Flags().IntVarP(&iterations, "iterations", "i", 1, "iterations")
	cmd.Flags().BoolVar(&savePolicy, "save-policy", false, "write best trial summary JSON")
	return cmd
}

func newTrialsCmd() *cobra.Command {
	var trialID int
	var limit int
	var pareto bool

	cmd := &cobra.Command{
		Use:   "trials",
		Short: "Show trial history",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()

			if cmd.Flags().Lookup("trial-id").Changed {
				for i := range b.Trials {
					t := &b.Trials[i]
					if t.ID == trialID {
						printTrialDetail(cmd, t)
						return nil
					}
				}
				return fmt.Errorf("trial #%d not found", trialID)
			}

			list := b.Trials
			if pareto {
				fmt.Fprintln(cmd.OutOrStdout(), "Pareto frontier:")
				list = b.Pareto
			} else {
				fmt.Fprintf(cmd.OutOrStdout(), "Recent trials (showing up to %d of %d)\n", limit, len(b.Trials))
				if limit > 0 && len(list) > limit {
					list = list[:limit]
				}
			}
			if len(list) == 0 {
				fmt.Fprintln(cmd.OutOrStdout(), "No trials")
				return nil
			}
			w := cmd.OutOrStdout()
			fmt.Fprintf(w, "%4s %-20s %8s %8s %8s %8s\n",
				"ID", "Policy", "Score", "Lat", "Cost", "Success")
			fmt.Fprintln(w, strings.Repeat("-", 72))
			for i := range list {
				t := &list[i]
				fmt.Fprintf(w, "%4d %-20.20s %8.4f %8.1f %8.5f %8.3f\n",
					t.ID, t.PolicyName, t.Score,
					t.Metrics["latency_p95"],
					t.Metrics["cost_per_req"],
					t.Metrics["task_success"],
				)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&trialID, "trial-id", 0, "show a single trial")
	cmd.Flags().IntVarP(&limit, "limit", "l", 20, "max rows for recent view")
	cmd.Flags().BoolVar(&pareto, "pareto", false, "show Pareto frontier")
	return cmd
}

func printTrialDetail(cmd *cobra.Command, t *core.Trial) {
	w := cmd.OutOrStdout()
	fmt.Fprintf(w, "Trial #%d:\n", t.ID)
	fmt.Fprintf(w, "  Policy: %s\n", t.PolicyName)
	fmt.Fprintf(w, "  Workload: %s\n", t.Workload)
	fmt.Fprintf(w, "  Score: %.4f\n", t.Score)
	fmt.Fprintf(w, "  Created: %s\n", t.CreatedAt.Format(time.RFC3339))
	fmt.Fprintln(w, "  Metrics:")
	for k, v := range t.Metrics {
		fmt.Fprintf(w, "    %s: %g\n", k, v)
	}
}

func newOptimizersCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "optimizers",
		Short: "List optimizers",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()
			w := cmd.OutOrStdout()
			fmt.Fprintln(w, "Available optimizers:")
			fmt.Fprintln(w, strings.Repeat("-", 50))
			for i, o := range b.Opts {
				fmt.Fprintf(w, "%d: %s\n", i, o.Name())
				meta := b.Meta[i]
				if meta.BestScore != nil {
					fmt.Fprintf(w, "   best_score: %g\n", *meta.BestScore)
				}
				for k, v := range o.GetState() {
					fmt.Fprintf(w, "   %s: %v\n", k, v)
				}
				fmt.Fprintln(w)
			}
			return nil
		},
	}
}

func newEvaluatorsCmd() *cobra.Command {
	var useSlug string
	cmd := &cobra.Command{
		Use:   "evaluators",
		Short: "List evaluators or set default (--use)",
		RunE: func(cmd *cobra.Command, args []string) error {
			names := evaluator.Names()
			if useSlug != "" {
				cfg, err := LoadConfig(cmd)
				if err != nil {
					return err
				}
				if _, err := evaluator.Get(useSlug, cfg); err != nil {
					return err
				}
				cfg.Evaluation.DefaultEvaluator = useSlug
				path, err := config.DefaultConfigPath()
				if err != nil {
					return err
				}
				if err := cfg.Save(path); err != nil {
					return err
				}
				fmt.Fprintf(cmd.OutOrStdout(), "Default evaluator set to %q (saved %s)\n", useSlug, path)
				return nil
			}
			w := cmd.OutOrStdout()
			fmt.Fprintln(w, "Available evaluators:")
			fmt.Fprintln(w, strings.Repeat("-", 50))
			for _, n := range names {
				fmt.Fprintf(w, "- %s\n", n)
			}
			return nil
		},
	}
	cmd.Flags().StringVar(&useSlug, "use", "", "set default evaluator slug and save config")
	return cmd
}

func newWorkloadsCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "workloads",
		Short: "List workloads",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()
			w := cmd.OutOrStdout()
			fmt.Fprintln(w, "Available workloads:")
			fmt.Fprintln(w, strings.Repeat("-", 50))
			for i, wl := range b.Workloads {
				fmt.Fprintf(w, "%d: %s\n", i, wl.Name)
				fmt.Fprintf(w, "   Items: %d\n", wl.Items)
				if wl.Description != "" {
					fmt.Fprintf(w, "   %s\n", wl.Description)
				}
				fmt.Fprintln(w)
			}
			return nil
		},
	}
}

func newAdoptCmd() *cobra.Command {
	var trialID int
	cmd := &cobra.Command{
		Use:   "adopt",
		Short: "Adopt a policy from a trial",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()
			if !b.AdoptPolicy(trialID) {
				fmt.Fprintln(cmd.OutOrStderr(), "Adopt failed (trial missing or guardrails).")
				os.Exit(1)
			}
			fmt.Fprintf(cmd.OutOrStdout(), "Adopted trial #%d\n", trialID)
			if b.ActivePolicy != nil {
				fmt.Fprintf(cmd.OutOrStdout(), "Active policy: %s\n", b.ActivePolicy.Name)
			}
			return nil
		},
	}
	cmd.Flags().IntVar(&trialID, "trial-id", 0, "trial id")
	_ = cmd.MarkFlagRequired("trial-id")
	return cmd
}

func newStatsCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "stats",
		Short: "Show backend statistics",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			defer b.Close()
			s := b.Stats()
			w := cmd.OutOrStdout()
			fmt.Fprintln(w, "Backend statistics:")
			fmt.Fprintln(w, strings.Repeat("-", 30))
			fmt.Fprintf(w, "Trials: %v\n", s["trial_count"])
			fmt.Fprintf(w, "Pareto frontier: %v\n", s["pareto_count"])
			fmt.Fprintf(w, "Optimizers: %v\n", s["optimizer_count"])
			fmt.Fprintf(w, "Workloads: %v\n", s["workload_count"])
			fmt.Fprintf(w, "Active policy: %v\n", s["active_policy"])
			fmt.Fprintf(w, "Storage: %v\n", s["storage_type"])
			fmt.Fprintf(w, "Evaluator: %v\n", s["evaluator"])
			if bs, ok := s["best_score"].(*float64); ok && bs != nil {
				fmt.Fprintf(w, "Best score: %.4f\n", *bs)
			}
			fmt.Fprintf(w, "Recent trials (7 days): %v\n", s["recent_trials"])
			return nil
		},
	}
}

func newResetCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "reset",
		Short: "Clear trials and policies from storage",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Fprint(cmd.OutOrStdout(), "This clears all trials and policies. Type 'yes' to continue: ")
			sc := bufio.NewScanner(os.Stdin)
			if !sc.Scan() {
				return nil
			}
			if strings.ToLower(strings.TrimSpace(sc.Text())) != "yes" {
				fmt.Fprintln(cmd.OutOrStdout(), "Cancelled")
				return nil
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
			if err := b.Reset(); err != nil {
				return err
			}
			fmt.Fprintln(cmd.OutOrStdout(), "Backend reset complete")
			return nil
		},
	}
	return cmd
}

func newServeCmd() *cobra.Command {
	var host string
	var port int
	cmd := &cobra.Command{
		Use:   "serve",
		Short: "Web server (not implemented)",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Fprintf(cmd.OutOrStdout(), "Web server not implemented (would bind %s:%d)\n", host, port)
		},
	}
	cmd.Flags().StringVar(&host, "host", "localhost", "host")
	cmd.Flags().IntVar(&port, "port", 8080, "port")
	return cmd
}

func newValidateConfigCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "validate-config",
		Short: "Validate a configuration file",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := config.Load(args[0])
			if err != nil {
				return err
			}
			w := cmd.OutOrStdout()
			fmt.Fprintf(w, "Configuration %q is valid.\n", args[0])
			fmt.Fprintf(w, "  Model: %s / %s\n", cfg.Model.Provider, cfg.Model.ModelName)
			fmt.Fprintf(w, "  Storage: %s\n", cfg.Storage.Backend)
			fmt.Fprintf(w, "  Experiments dir: %s\n", cfg.Storage.ExperimentsDir)
			return nil
		},
	}
}

func newTUICmd() *cobra.Command {
	var demo bool
	var scenario string
	cmd := &cobra.Command{
		Use:   "tui",
		Short: "Start the Bubble Tea TUI",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := LoadConfig(cmd)
			if err != nil {
				return err
			}
			if demo {
				cfg = cloneCfgForDemo(cfg)
			}
			b, err := backend.New(cfg)
			if err != nil {
				return err
			}
			if demo {
				backend.SeedDemo(b, scenario)
			}
			defer b.Close()
			return RunTUI(b, demo, scenario)
		},
	}
	cmd.Flags().BoolVar(&demo, "demo", false, "load demo data (uses memory storage)")
	cmd.Flags().StringVar(&scenario, "scenario", "leetcode", "demo scenario label")
	return cmd
}

func cloneCfgForDemo(cfg *config.Config) *config.Config {
	cp := *cfg
	cp.Storage = cfg.Storage
	cp.Storage.Backend = "memory"
	cp.ExpandPaths()
	return &cp
}

func newDoctorCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "doctor",
		Short: "Print version and config path hints",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Fprintf(cmd.OutOrStdout(), "cie version %s\n", Version)
			if p, err := config.DefaultConfigPath(); err == nil {
				fmt.Fprintf(cmd.OutOrStdout(), "Default config: %s\n", p)
			}
		},
	}
}
