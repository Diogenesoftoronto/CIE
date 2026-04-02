package optimizer

// WeightedObjectiveScore mirrors the backend scalar objective (lower is better)
// using the default metric subset.
func WeightedObjectiveScore(m map[string]float64) float64 {
	w := map[string]float64{
		"latency_p95":     0.001,
		"cost_per_req":    0.5,
		"task_success":    -1,
		"context_usage":   0.2,
		"tool_error_rate": 0.8,
	}
	var s float64
	for k, wt := range w {
		s += wt * m[k]
	}
	return s
}
