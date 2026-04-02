package benchmark

import "time"

// TaskMetrics captures execution stats for a task.
type TaskMetrics struct {
	TaskID           string
	Success          bool
	CompletionStatus string
	Duration         time.Duration
	Attempts         int
	ToolCalls        int
	Errors           []string
}
