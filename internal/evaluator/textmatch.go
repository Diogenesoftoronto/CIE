package evaluator

import (
	"fmt"
	"math"
	"strings"
	"time"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
)

// TextMatch scores synthetic “model outputs” with Levenshtein-based similarity.
// No external HTTP calls — outputs are derived from policy parameters for repeatable runs.
type TextMatch struct {
	cfg *config.Config
}

// NewTextMatch constructs the evaluator.
func NewTextMatch(cfg *config.Config) *TextMatch {
	return &TextMatch{cfg: cfg}
}

func (t *TextMatch) Name() string { return "text-match" }

func (t *TextMatch) SupportedMetrics() []string {
	return []string{
		"latency_p95", "cost_per_req", "task_success", "context_usage", "tool_error_rate",
		"throughput", "memory_usage", "cpu_usage",
		"text_similarity", "text_exact_match", "text_levenshtein",
	}
}

func (t *TextMatch) ValidateWorkload(w *core.Workload) bool {
	if w.Config == nil {
		return false
	}
	if _, ok := w.Config["cases"]; ok {
		return true
	}
	ds, _ := w.Config["dataset"].(string)
	return ds == "" || ds == "text"
}

type textCase struct {
	Task      string `json:"task"`
	Prompt    string `json:"prompt"`
	Reference string `json:"reference"`
	Guidance  string `json:"guidance"`
}

func (t *TextMatch) Run(policy *core.Policy, workload *core.Workload) (map[string]float64, error) {
	cases := resolveCases(workload)
	if len(cases) == 0 {
		return nil, fmt.Errorf("text-match: no cases for workload %q", workload.Name)
	}
	start := time.Now()
	var latencies []float64
	var sims, exacts, levs []float64

	quality := policyQuality(policy)

	for _, c := range cases {
		t0 := time.Now()
		cand := synthesizeCandidate(c.Reference, c.Prompt, quality)
		latencies = append(latencies, float64(time.Since(t0).Microseconds())/1000.0)
		cmp := compareStrings(cand, c.Reference)
		sims = append(sims, cmp.similarity)
		exacts = append(exacts, cmp.exact)
		levs = append(levs, cmp.levNorm)
	}

	elapsed := time.Since(start).Seconds()
	avg := mean(sims)
	avgEx := mean(exacts)
	avgLev := mean(levs)
	latP95 := percentile(latencies, 95)

	maxTok := 4096.0
	if t.cfg != nil && t.cfg.Model.MaxTokens > 0 {
		maxTok = float64(t.cfg.Model.MaxTokens)
	}
	tokEst := averagePromptLen(cases)

	return map[string]float64{
		"latency_p95":      latP95,
		"cost_per_req":     0.0005 + 0.00002*float64(len(cases)),
		"task_success":     avg,
		"context_usage":    min64(1, tokEst/maxTok),
		"tool_error_rate":  max64(0, 1-avg),
		"throughput":       float64(len(cases)) / math.Max(elapsed, 1e-6),
		"memory_usage":     0.35 + 0.05*float64(len(policy.Params)),
		"cpu_usage":        min64(0.95, 0.4+0.03*float64(len(cases))),
		"text_similarity":  avg,
		"text_exact_match": avgEx,
		"text_levenshtein": avgLev,
	}, nil
}

func resolveCases(w *core.Workload) []textCase {
	if w.Config == nil {
		return defaultTextCases()
	}
	raw, ok := w.Config["cases"]
	if !ok {
		if ds, _ := w.Config["dataset"].(string); ds == "text" || ds == "" {
			return defaultTextCases()
		}
		return nil
	}
	arr, ok := raw.([]any)
	if !ok {
		return nil
	}
	var out []textCase
	for _, it := range arr {
		m, ok := it.(map[string]any)
		if !ok {
			continue
		}
		tc := textCase{
			Task:      asString(m["task"]),
			Prompt:    asString(m["prompt"]),
			Reference: asString(m["reference"]),
			Guidance:  asString(m["guidance"]),
		}
		if tc.Reference != "" {
			out = append(out, tc)
		}
	}
	if len(out) == 0 {
		return defaultTextCases()
	}
	return out
}

func defaultTextCases() []textCase {
	return []textCase{
		{Task: "Sentiment", Prompt: "positive or negative?", Reference: "positive"},
		{Task: "Short answer", Prompt: "95th latency metric?", Reference: "latency_p95"},
	}
}

func asString(v any) string {
	switch x := v.(type) {
	case string:
		return x
	case fmt.Stringer:
		return x.String()
	default:
		return ""
	}
}

func policyQuality(p *core.Policy) float64 {
	if p.Params == nil {
		return 0.55
	}
	q := 0.55
	if v, ok := floatParam(p.Params, "temperature"); ok {
		q += (1.0 - v) * 0.25
	}
	if v, ok := floatParam(p.Params, "prune_ratio"); ok {
		q -= v * 0.15
	}
	if v, ok := floatParam(p.Params, "learning_rate"); ok {
		q += min64(0.15, v)
	}
	return math.Max(0.05, math.Min(0.98, q))
}

func synthesizeCandidate(reference, prompt string, quality float64) string {
	// Corrupt reference proportionally to (1-quality)
	r := []rune(reference)
	if len(r) == 0 {
		return prompt[:min(len(prompt), 12)]
	}
	steps := int(math.Ceil(float64(len(r)) * (1 - quality) * 0.8))
	out := append([]rune(nil), r...)
	for i := 0; i < steps && len(out) > 0; i++ {
		op := (i + len(prompt)) % 3
		switch op {
		case 0: // delete
			out = append(out[:i%len(out)], out[i%len(out)+1:]...)
		case 1: // substitute
			pos := i % len(out)
			out[pos] = rune('a' + (i % 26))
		default: // insert
			pos := i % max(1, len(out))
			ch := rune(' ')
			if len(prompt) > 0 {
				ch = rune(prompt[i%len(prompt)])
			}
			out = append(out[:pos], append([]rune{ch}, out[pos:]...)...)
		}
		if len(out) == 0 {
			break
		}
	}
	return string(out)
}

type cmp struct {
	similarity float64
	exact      float64
	levNorm    float64
}

func compareStrings(a, b string) cmp {
	if a == b {
		return cmp{similarity: 1, exact: 1, levNorm: 1}
	}
	d := levenshtein([]rune(strings.ToLower(a)), []rune(strings.ToLower(b)))
	maxLen := max(len([]rune(a)), len([]rune(b)))
	if maxLen == 0 {
		return cmp{}
	}
	levNorm := 1.0 - float64(d)/float64(maxLen)
	levNorm = math.Max(0, math.Min(1, levNorm))
	// similarity: Jaccard on word tokens + lev blend
	sim := 0.6*levNorm + 0.4*jaccardWords(a, b)
	return cmp{similarity: sim, exact: 0, levNorm: levNorm}
}

func jaccardWords(a, b string) float64 {
	ta := wordSet(a)
	tb := wordSet(b)
	if len(ta) == 0 && len(tb) == 0 {
		return 1
	}
	inter := 0
	for w := range ta {
		if tb[w] {
			inter++
		}
	}
	union := len(ta) + len(tb) - inter
	if union == 0 {
		return 0
	}
	return float64(inter) / float64(union)
}

func wordSet(s string) map[string]bool {
	m := map[string]bool{}
	for _, w := range strings.Fields(strings.ToLower(s)) {
		if w != "" {
			m[w] = true
		}
	}
	return m
}

func levenshtein(a, b []rune) int {
	if len(a) == 0 {
		return len(b)
	}
	if len(b) == 0 {
		return len(a)
	}
	prev := make([]int, len(b)+1)
	for j := 0; j <= len(b); j++ {
		prev[j] = j
	}
	for i := 1; i <= len(a); i++ {
		cur := make([]int, len(b)+1)
		cur[0] = i
		for j := 1; j <= len(b); j++ {
			cost := 0
			if a[i-1] != b[j-1] {
				cost = 1
			}
			cur[j] = minInt(
				cur[j-1]+1,
				minInt(prev[j]+1, prev[j-1]+cost),
			)
		}
		prev = cur
	}
	return prev[len(b)]
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func mean(xs []float64) float64 {
	if len(xs) == 0 {
		return 0
	}
	s := 0.0
	for _, x := range xs {
		s += x
	}
	return s / float64(len(xs))
}

func percentile(xs []float64, p float64) float64 {
	if len(xs) == 0 {
		return 0
	}
	// naive copy sort
	cp := append([]float64(nil), xs...)
	for i := 0; i < len(cp); i++ {
		for j := i + 1; j < len(cp); j++ {
			if cp[j] < cp[i] {
				cp[i], cp[j] = cp[j], cp[i]
			}
		}
	}
	idx := int(math.Ceil(float64(len(cp))*p/100)) - 1
	if idx < 0 {
		idx = 0
	}
	if idx >= len(cp) {
		idx = len(cp) - 1
	}
	return cp[idx]
}

func averagePromptLen(cases []textCase) float64 {
	if len(cases) == 0 {
		return 0
	}
	s := 0.0
	for _, c := range cases {
		s += float64(len(c.Prompt) + len(c.Reference))
	}
	return s / float64(len(cases))
}

func max64(a, b float64) float64 {
	if a > b {
		return a
	}
	return b
}

func min64(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
