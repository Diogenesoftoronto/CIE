package benchmark

import (
	"context"
	"fmt"
	"time"
)

// Result is the outcome of one task.
type Result struct {
	Task    Task
	Metrics TaskMetrics
}

// Runner orchestrates benchmark tasks (ported from Python BenchmarkRunner).
type Runner struct {
	ModelName      string
	MaxRetries     int
	TimeoutPerTask time.Duration
	RunID          string
}

// NewRunner creates a runner with defaults.
func NewRunner(modelName string) *Runner {
	return &Runner{
		ModelName:      modelName,
		MaxRetries:     2,
		TimeoutPerTask: 120 * time.Second,
		RunID:          fmt.Sprintf("%d", time.Now().UnixNano()),
	}
}

// Executor runs a single task (e.g. external agent). Returns success, output, errors.
type Executor func(ctx context.Context, t Task) (bool, string, []string)

// RunAll executes tasks sequentially with the given executor.
func (r *Runner) RunAll(ctx context.Context, tasks []Task, exec Executor) ([]Result, error) {
	if exec == nil {
		return nil, fmt.Errorf("executor required")
	}
	var out []Result
	for _, task := range tasks {
		select {
		case <-ctx.Done():
			return out, ctx.Err()
		default:
		}
		out = append(out, r.runOne(ctx, task, exec))
	}
	return out, nil
}

func (r *Runner) runOne(ctx context.Context, task Task, exec Executor) Result {
	tctx, cancel := context.WithTimeout(ctx, r.TimeoutPerTask)
	defer cancel()
	start := time.Now()
	ok, _, errs := exec(tctx, task)
	dur := time.Since(start)
	st := "completed"
	if tctx.Err() == context.DeadlineExceeded {
		st = "timeout"
		ok = false
		if errs == nil {
			errs = []string{"deadline exceeded"}
		}
	} else if !ok {
		st = "failed"
	}
	return Result{
		Task: task,
		Metrics: TaskMetrics{
			TaskID:           task.ID,
			Success:          ok,
			CompletionStatus: st,
			Duration:         dur,
			Attempts:         1,
			Errors:           errs,
		},
	}
}

// DefaultStubExecutor succeeds on easy/trivial tasks deterministically (for CI / smoke).
func DefaultStubExecutor(t Task) (bool, string, []string) {
	switch t.Difficulty {
	case Trivial, Easy:
		return true, "stub-ok", nil
	default:
		return false, "stub-skip", []string{"difficulty not met in stub"}
	}
}

// StubExecutorContext wraps DefaultStubExecutor.
func StubExecutorContext() Executor {
	return func(ctx context.Context, t Task) (bool, string, []string) {
		_ = ctx
		return DefaultStubExecutor(t)
	}
}

// PassRate returns fraction of successful results.
func PassRate(rs []Result) float64 {
	if len(rs) == 0 {
		return 0
	}
	n := 0
	for i := range rs {
		if rs[i].Metrics.Success {
			n++
		}
	}
	return float64(n) / float64(len(rs))
}
