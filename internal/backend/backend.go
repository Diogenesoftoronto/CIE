package backend

import (
	"fmt"
	"time"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
	"github.com/cie-team/cie/internal/evaluator"
	"github.com/cie-team/cie/internal/optimizer"
	"github.com/cie-team/cie/internal/storage"
)

// Backend is the CIEBackend equivalent.
type Backend struct {
	Config *config.Config

	stor     storage.Backend
	eval     evaluator.Evaluator
	evalSlug string
	Opts     []optimizer.Optimizer
	Meta     []OptimizerMeta

	Workloads    []core.Workload
	Trials       []core.Trial
	Pareto       []core.Trial
	ActivePolicy *core.Policy

	trialID int
}

// OptimizerMeta tracks per-optimizer bookkeeping.
type OptimizerMeta struct {
	BestScore  *float64
	ArtifactID *string
}

// New constructs a backend from configuration.
func New(cfg *config.Config) (*Backend, error) {
	if cfg == nil {
		cfg = config.Default()
	}
	cfg.ApplyEnvAPIKeys()
	cfg.ExpandPaths()

	var stor storage.Backend
	var err error
	switch cfg.Storage.Backend {
	case "memory":
		stor = storage.NewMemory()
	case "json":
		stor, err = storage.NewJSON(cfg.Storage.ExperimentsDir)
	case "sqlite":
		stor, err = storage.NewSQLite(cfg.Storage.DatabasePath)
	default:
		return nil, fmt.Errorf("unknown storage backend %q", cfg.Storage.Backend)
	}
	if err != nil {
		return nil, err
	}

	ev, err := evaluator.Get(cfg.Evaluation.DefaultEvaluator, cfg)
	if err != nil {
		return nil, err
	}

	wl, err := loadDefaultWorkloads()
	if err != nil {
		return nil, err
	}

	opts := optimizer.NewDefaults(cfg)
	meta := make([]OptimizerMeta, len(opts))
	for i := range meta {
		meta[i] = OptimizerMeta{}
	}

	b := &Backend{
		Config:    cfg,
		stor:      stor,
		eval:      ev,
		evalSlug:  cfg.Evaluation.DefaultEvaluator,
		Opts:      opts,
		Meta:      meta,
		Workloads: wl,
		Trials:    nil,
		Pareto:    nil,
		trialID:   0,
	}
	if err := b.reloadTrials(); err != nil {
		return nil, err
	}
	return b, nil
}

// Reload refreshes trials from storage (e.g. after external changes).
func (b *Backend) Reload() error {
	return b.reloadTrials()
}

func (b *Backend) reloadTrials() error {
	tr, err := b.stor.GetTrials(0)
	if err != nil {
		return err
	}
	b.Trials = tr
	maxID := 0
	for _, t := range b.Trials {
		if t.ID > maxID {
			maxID = t.ID
		}
	}
	b.trialID = maxID
	b.rebuildPareto()
	return nil
}

// Score is the weighted linear combination (lower is better).
func (b *Backend) Score(metrics map[string]float64) float64 {
	var s float64
	w := b.Config.Evaluation.MetricWeights
	for k, wt := range w {
		s += wt * metrics[k]
	}
	// round like Python
	return float64(int64(s*1e6+0.5)) / 1e6
}

func dominates(a, b *core.Trial) bool {
	la := a.Metrics["latency_p95"]
	ca := a.Metrics["cost_per_req"]
	qa := 1 - a.Metrics["task_success"]
	lb := b.Metrics["latency_p95"]
	cb := b.Metrics["cost_per_req"]
	qb := 1 - b.Metrics["task_success"]
	better := (la <= lb && ca <= cb && qa <= qb) && (la < lb || ca < cb || qa < qb)
	return better
}

func (b *Backend) rebuildPareto() {
	if len(b.Trials) == 0 {
		b.Pareto = nil
		return
	}
	var front []core.Trial
	for i := range b.Trials {
		t := b.Trials[i]
		dominated := false
		for j := range b.Trials {
			if i == j {
				continue
			}
			if dominates(&b.Trials[j], &t) {
				dominated = true
				break
			}
		}
		if !dominated {
			front = append(front, t)
		}
	}
	seen := map[int]bool{}
	var uniq []core.Trial
	for _, t := range front {
		if seen[t.ID] {
			continue
		}
		seen[t.ID] = true
		uniq = append(uniq, t)
	}
	b.Pareto = uniq
}

// OptimizerName returns the Nth optimizer name.
func (b *Backend) OptimizerName(i int) string {
	if i < 0 || i >= len(b.Opts) {
		return ""
	}
	return b.Opts[i].Name()
}

// ProposeOnce asks optimizer i for a policy.
func (b *Backend) ProposeOnce(optimizerIndex int) (*core.Policy, error) {
	if optimizerIndex < 0 || optimizerIndex >= len(b.Opts) {
		return nil, fmt.Errorf("invalid optimizer index %d", optimizerIndex)
	}
	state := map[string]any{
		"trials":        b.Trials,
		"pareto":        b.Pareto,
		"active_policy": b.ActivePolicy,
	}
	return b.Opts[optimizerIndex].Propose(state), nil
}

// EvalPolicy runs evaluation and records a trial.
func (b *Backend) EvalPolicy(policy *core.Policy, workloadIndex int) (*core.Trial, error) {
	if workloadIndex < 0 || workloadIndex >= len(b.Workloads) {
		return nil, fmt.Errorf("invalid workload index %d", workloadIndex)
	}
	w := &b.Workloads[workloadIndex]
	if !b.eval.ValidateWorkload(w) {
		return nil, fmt.Errorf("evaluator %q cannot run workload %q", b.evalSlug, w.Name)
	}
	metrics, err := b.eval.Run(policy, w)
	if err != nil {
		return nil, err
	}
	score := b.Score(metrics)
	b.trialID++
	var art *string
	if a, ok := policy.Params["artifact"].(string); ok && a != "" {
		art = &a
	}
	trial := &core.Trial{
		ID:         b.trialID,
		PolicyName: policy.Name,
		Metrics:    metrics,
		Score:      score,
		Workload:   w.Name,
		CreatedAt:  time.Now().UTC(),
		ArtifactID: art,
		Metadata: map[string]any{
			"workload_config": w.Config,
		},
	}
	b.Trials = append(b.Trials, *trial)
	if err := b.stor.SaveTrial(trial); err != nil {
		return nil, err
	}

	nameToIdx := map[string]int{}
	for i, o := range b.Opts {
		nameToIdx[o.Name()] = i
	}
	if idx, ok := nameToIdx[policy.Name]; ok {
		best := b.Meta[idx].BestScore
		if best == nil || score < *best {
			v := score
			b.Meta[idx].BestScore = &v
			b.Meta[idx].ArtifactID = art
		}
		b.Opts[idx].Observe(policy, metrics)
	}
	b.rebuildPareto()
	return trial, nil
}

// AdoptPolicy applies guardrails and sets active policy.
func (b *Backend) AdoptPolicy(trialID int) bool {
	var trial *core.Trial
	for i := range b.Trials {
		if b.Trials[i].ID == trialID {
			trial = &b.Trials[i]
			break
		}
	}
	if trial == nil {
		return false
	}
	ev := b.Config.Evaluation
	if trial.Metrics["tool_error_rate"] > ev.MaxToolErrorRate {
		return false
	}
	if trial.Metrics["task_success"] < ev.MinTaskSuccessRate {
		return false
	}
	if trial.Metrics["latency_p95"] > ev.MaxLatencyP95 {
		return false
	}
	params := map[string]any{
		"adopted_from_trial": float64(trial.ID),
		"original_policy":    trial.PolicyName,
	}
	if trial.ArtifactID != nil {
		params["artifact"] = *trial.ArtifactID
	}
	adopted := &core.Policy{
		Name:   fmt.Sprintf("%s@adopted", trial.PolicyName),
		Params: params,
		Actions: []string{
			fmt.Sprintf("apply.diff(trial_id=%d)", trial.ID),
			"enable.cache(optimized)",
			"limit.tools(safe)",
			"monitor.metrics(enabled)",
		},
		CreatedAt: time.Now().UTC(),
		Metadata: map[string]any{
			"trial_metrics": trial.Metrics,
			"trial_score":   trial.Score,
		},
	}
	_ = b.stor.SavePolicy(adopted)
	b.ActivePolicy = adopted
	return true
}

// Stats summary map for CLI.
func (b *Backend) Stats() map[string]any {
	var best *float64
	for i := range b.Trials {
		sc := b.Trials[i].Score
		if best == nil || sc < *best {
			v := sc
			best = &v
		}
	}
	recent := 0
	cutoff := time.Now().AddDate(0, 0, -7)
	for i := range b.Trials {
		if b.Trials[i].CreatedAt.After(cutoff) {
			recent++
		}
	}
	return map[string]any{
		"trial_count":     len(b.Trials),
		"pareto_count":    len(b.Pareto),
		"optimizer_count": len(b.Opts),
		"workload_count":  len(b.Workloads),
		"active_policy":   b.ActivePolicy != nil,
		"storage_type":    b.Config.Storage.Backend,
		"evaluator":       b.evalSlug,
		"best_score":      best,
		"recent_trials":   recent,
	}
}

// Reset clears trials and memory state (and storage when supported).
func (b *Backend) Reset() error {
	b.Trials = nil
	b.Pareto = nil
	b.ActivePolicy = nil
	b.trialID = 0
	for i := range b.Meta {
		b.Meta[i] = OptimizerMeta{}
	}
	for _, o := range b.Opts {
		o.Reset()
	}
	return b.stor.ClearAll()
}

// Close releases the storage layer.
func (b *Backend) Close() error {
	return b.stor.Close()
}

// SetEvaluator swaps the active evaluator (updates in-memory only; caller persists config).
func (b *Backend) SetEvaluator(slug string) error {
	ev, err := evaluator.Get(slug, b.Config)
	if err != nil {
		return err
	}
	b.eval = ev
	b.evalSlug = slug
	b.Config.Evaluation.DefaultEvaluator = slug
	return nil
}
