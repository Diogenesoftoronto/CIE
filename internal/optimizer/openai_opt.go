package optimizer

import (
	"context"
	"encoding/json"
	"fmt"
	"math/rand/v2"
	"os"
	"strings"
	"time"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/core"
	"github.com/cie-team/cie/internal/llm"
	"github.com/cie-team/cie/internal/trace"
)

// OpenAIPolicyOptimizer proposes JSON policy parameters via an OpenAI-compatible chat API
// (OpenAI, Kimi/Moonshot, or any same-shaped endpoint). This replaces the old Python DSPy
// module with a single-shot JSON policy synthesis prompt (DSPy runtime not required).
type OpenAIPolicyOptimizer struct {
	cfg       *config.Config
	kShots    int
	model     string
	iter      int
	rng       *rand.Rand
	bootstrap []bootstrapEx
	status    string
}

type bootstrapEx struct {
	Params  map[string]any
	Metrics map[string]float64
	Score   float64
}

const openAIPolicyOptimizerName = "OpenAI:PolicyJSON"

// NewOpenAIPolicyOptimizer builds the LLM-driven optimizer.
func NewOpenAIPolicyOptimizer(cfg *config.Config) *OpenAIPolicyOptimizer {
	if cfg == nil {
		cfg = config.Default()
	}
	ks := cfg.Optimization.KShots
	if ks <= 0 {
		ks = 8
	}
	src := rand.NewPCG(uint64(time.Now().UnixNano()), 0xbadf00d)
	return &OpenAIPolicyOptimizer{
		cfg:    cfg,
		kShots: ks,
		model:  cfg.Model.ModelName,
		rng:    rand.New(src),
		status: "idle",
	}
}

func (o *OpenAIPolicyOptimizer) Name() string { return openAIPolicyOptimizerName }

func (o *OpenAIPolicyOptimizer) Reset() {
	o.iter = 0
	o.bootstrap = nil
	o.status = "idle"
}

func (o *OpenAIPolicyOptimizer) GetState() map[string]any {
	return map[string]any{
		"k_shots":              o.kShots,
		"model":                o.model,
		"bootstrap_examples":   len(o.bootstrap),
		"llm_optimizer_status": o.status,
		"iteration":            o.iter,
	}
}

func (o *OpenAIPolicyOptimizer) Observe(policy *core.Policy, metrics map[string]float64) {
	score := WeightedObjectiveScore(metrics)
	th := o.cfg.Optimization.BootstrapMinSuccess
	if th <= 0 {
		th = 0.78
	}
	if metrics["task_success"] >= th {
		ex := bootstrapEx{Params: cloneMap(policy.Params), Metrics: metrics, Score: score}
		o.bootstrap = append(o.bootstrap, ex)
		if len(o.bootstrap) > o.kShots {
			o.bootstrap = o.bootstrap[len(o.bootstrap)-o.kShots:]
		}
	}
}

func (o *OpenAIPolicyOptimizer) Propose(state map[string]any) *core.Policy {
	o.iter++
	artifact := fmt.Sprintf("llm-%d-%d", time.Now().UnixMilli(), o.iter)
	system := "You are an optimization expert. Return a single JSON object only with numeric policy fields: " +
		"temperature (0.1-1), max_tokens (100-4000), prune_ratio (0-0.8), learning_rate (0.001-0.1), " +
		"batch_size (1-32), dropout_rate (0-0.5), optional prompt_template (short string), context_strategy (short string). " +
		"No markdown fences."
	user := o.composePrompt(state, artifact)

	apiKey := strings.TrimSpace(o.cfg.Model.APIKey)
	provider := strings.ToLower(strings.TrimSpace(o.cfg.Model.Provider))

	cfgLLM := *o.cfg
	cfgLLM.Model = o.cfg.Model
	if provider == "kimi" && !strings.Contains(strings.ToLower(cfgLLM.Model.ModelName), "moonshot") {
		cfgLLM.Model.ModelName = "moonshot-v1-8k"
	}
	cfgLLM.ApplyEnvAPIKeys()

	regKeyPre := cfgLLM.GenAIRegistryKey()
	keyOptional := regKeyPre == "ollama" || regKeyPre == "llamacpp"

	var blob string
	if regKeyPre != "" && provider != "mock" && provider != "" && (apiKey != "" || keyOptional) {
		timeout := time.Duration(o.cfg.Model.TimeoutSecs) * time.Second
		if timeout <= 0 {
			timeout = 120 * time.Second
		}
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()
		prov, regKey, perr := llm.NewProvider(ctx, &cfgLLM)
		maxTok := o.cfg.Model.MaxTokens
		if maxTok <= 0 {
			maxTok = 1000
		}
		temp := o.cfg.Model.Temperature
		if temp <= 0 {
			temp = 0.35
		}
		if perr != nil {
			o.status = "provider_error:" + truncateStr(perr.Error(), 80)
		} else if prov == nil {
			o.status = "no_genai_provider"
		} else {
			res, gerr := llm.ChatText(ctx, prov, regKey, system, user, temp, int64(minI(1000, maxTok)))
			if gerr != nil {
				o.status = "api_error:" + truncateStr(gerr.Error(), 80)
			} else {
				blob = llm.ResultText(res)
				o.status = "ok"
			}
			if td := strings.TrimSpace(os.Getenv("CIE_TRACE_DIR")); td != "" && gerr == nil {
				_ = trace.WriteLLMSession(td, openAIPolicyOptimizerName, &cfgLLM, regKey, system, user, res)
			}
		}
	} else {
		o.status = "no_api_key"
	}

	params := parsePolicyJSON(blob)
	if len(params) == 0 {
		params = o.fallbackParams(artifact)
		if o.status == "ok" {
			o.status = "fallback_params"
		}
	}
	params["artifact"] = artifact
	params["k_shots"] = float64(o.kShots)
	params["model"] = cfgLLM.Model.ModelName
	if rk := cfgLLM.GenAIRegistryKey(); rk != "" {
		params["engine"] = "genai:" + rk
	} else {
		params["engine"] = "genai"
	}

	return &core.Policy{
		Name:      o.Name(),
		Params:    params,
		Actions:   actionsFromOpenAIParams(params),
		CreatedAt: time.Now().UTC(),
		Metadata: map[string]any{
			"optimizer":  o.Name(),
			"llm_status": o.status,
			"provider":   provider,
		},
	}
}

func (o *OpenAIPolicyOptimizer) fallbackParams(artifact string) map[string]any {
	p := randomParams(o.rng, defaultRanges())
	p["artifact"] = artifact
	p["strategy"] = "fallback_heuristic"
	return p
}

func (o *OpenAIPolicyOptimizer) composePrompt(state map[string]any, artifact string) string {
	var b strings.Builder
	fmt.Fprintf(&b, "Produce policy parameters as JSON. artifact_hint=%q\n", artifact)
	fmt.Fprintf(&b, "Target model: %s (k_shots=%d)\n", o.model, o.kShots)
	b.WriteString("Metric weights:\n")
	for k, w := range o.cfg.Evaluation.MetricWeights {
		fmt.Fprintf(&b, "- %s: %g\n", k, w)
	}
	if ap, ok := state["active_policy"].(*core.Policy); ok && ap != nil {
		fmt.Fprintf(&b, "Active policy: %s\n", ap.Name)
	}
	if trials, ok := state["trials"].([]core.Trial); ok && len(trials) > 0 {
		b.WriteString("Recent trials:\n")
		n := len(trials)
		start := 0
		if n > 8 {
			start = n - 8
		}
		for _, tr := range trials[start:] {
			fmt.Fprintf(&b, "- score=%.4f success=%.3f latency=%.1f cost=%.5f\n",
				tr.Score, tr.Metrics["task_success"], tr.Metrics["latency_p95"], tr.Metrics["cost_per_req"])
		}
	}
	if len(o.bootstrap) > 0 {
		b.WriteString("Good bootstrap examples (high task_success):\n")
		for _, ex := range o.bootstrap {
			pj, _ := json.Marshal(ex.Params)
			fmt.Fprintf(&b, "- params=%s score=%.4f success=%.3f\n", pj, ex.Score, ex.Metrics["task_success"])
		}
	}
	return b.String()
}

func actionsFromOpenAIParams(p map[string]any) []string {
	a := []string{
		fmt.Sprintf("openai.policy(artifact=%v)", p["artifact"]),
	}
	if pt, ok := p["prompt_template"].(string); ok && pt != "" {
		a = append(a, "prompt.use_template("+truncateStr(pt, 40))
	}
	if cs, ok := p["context_strategy"].(string); ok && cs != "" {
		a = append(a, "context.set_strategy("+truncateStr(cs, 40))
	}
	return a
}

func parsePolicyJSON(blob string) map[string]any {
	text := strings.TrimSpace(blob)
	if text == "" {
		return nil
	}
	if strings.HasPrefix(text, "```") {
		text = strings.TrimPrefix(text, "```")
		text = strings.TrimSpace(text)
		if strings.HasPrefix(strings.ToLower(text), "json") {
			text = strings.TrimSpace(text[4:])
		}
		text = strings.TrimSuffix(text, "```")
		text = strings.TrimSpace(text)
	}
	var m map[string]any
	if err := json.Unmarshal([]byte(text), &m); err == nil && len(m) > 0 {
		return m
	}
	i, j := strings.Index(text, "{"), strings.LastIndex(text, "}")
	if i >= 0 && j > i {
		if err := json.Unmarshal([]byte(text[i:j+1]), &m); err == nil && len(m) > 0 {
			return m
		}
	}
	return nil
}

func minI(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func truncateStr(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}
