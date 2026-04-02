package benchmark

// DefaultTasks returns a small built-in suite (aligned with former Python templates).
func DefaultTasks() []Task {
	return []Task{
		{
			ID: "trivial_read_file", Title: "Read and summarize",
			Description: "Navigate repo and summarize a small file.",
			Category:    CatNavigation, Difficulty: Trivial,
			Objective:    "Open README and list two features.",
			SuccessLines: []string{"mentions features"},
			EstMinutes:   2, MaxToolCalls: 15, Tags: []string{"read"},
		},
		{
			ID: "easy_cli_check", Title: "CLI smoke",
			Description: "Run cie doctor and interpret output.",
			Category:    CatTesting, Difficulty: Easy,
			Objective:    "Verify cie binary responds.",
			SuccessLines: []string{"exit 0"},
			EstMinutes:   3, MaxToolCalls: 10, Tags: []string{"cli"},
		},
		{
			ID: "medium_optimize_loop", Title: "Optimization loop",
			Description: "Run optimize with mock evaluator.",
			Category:    CatComprehension, Difficulty: Medium,
			Objective:    "Produce trials with improving scores.",
			SuccessLines: []string{"trials > 0"},
			EstMinutes:   10, MaxToolCalls: 25, Tags: []string{"optimize"},
		},
	}
}
