package benchmark

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/llm"
	"github.com/cie-team/cie/internal/trace"
)

// taskGenResponse is the shape we ask the model for in harness runs.
type taskGenResponse struct {
	Done    bool   `json:"done"`
	Summary string `json:"summary"`
}

// GenAIExecutor runs each task as a single chat turn via maruel/genai (same registry as the TUI/optimizer).
// traceDir may be empty; otherwise prompt/response minitrace JSON is written (CIE_TRACE_DIR convention).
func GenAIExecutor(cfg *config.Config, traceDir string) Executor {
	return func(ctx context.Context, t Task) (bool, string, []string) {
		if cfg == nil {
			cfg = config.Default()
		}
		runCfg := *cfg
		runCfg.ApplyEnvAPIKeys()
		prov, regKey, perr := llm.NewProvider(ctx, &runCfg)
		if perr != nil {
			return false, "", []string{fmt.Sprintf("genai provider: %v", perr)}
		}
		if prov == nil {
			return false, "", []string{"genai: no provider (set model.provider / genai_provider and API key)"}
		}
		system := "You are executing an agent benchmark task. Reply with JSON only: {\"done\": true|false, \"summary\": string}." +
			" Set done=true if the objective is plausibly satisfied from the description alone (dry run); false if not."
		user := formatTaskPrompt(t)
		temp := runCfg.Model.Temperature
		if temp <= 0 {
			temp = 0.2
		}
		maxTok := int64(runCfg.Model.MaxTokens)
		if maxTok <= 0 {
			maxTok = 512
		}
		res, gerr := llm.ChatText(ctx, prov, regKey, system, user, temp, maxTok)
		if gerr != nil {
			return false, "", []string{fmt.Sprintf("genai chat: %v", gerr)}
		}
		text := strings.TrimSpace(llm.ResultText(res))
		if td := strings.TrimSpace(traceDir); td != "" {
			_ = trace.WriteLLMSession(td, "benchmark:"+t.ID, &runCfg, regKey, system, user, res)
		}
		var parsed taskGenResponse
		if err := json.Unmarshal([]byte(text), &parsed); err == nil {
			return parsed.Done, parsed.Summary, nil
		}
		// Heuristic: model returned non-JSON prose — treat non-empty reply as partial progress.
		if text != "" {
			return true, text, nil
		}
		return false, text, []string{"empty model reply"}
	}
}

func formatTaskPrompt(t Task) string {
	var b strings.Builder
	fmt.Fprintf(&b, "task_id=%s\n", t.ID)
	fmt.Fprintf(&b, "title=%s\n", t.Title)
	fmt.Fprintf(&b, "difficulty=%s\n", t.Difficulty)
	fmt.Fprintf(&b, "objective=%s\n", t.Objective)
	fmt.Fprintf(&b, "description=%s\n", t.Description)
	if len(t.SuccessLines) > 0 {
		fmt.Fprintf(&b, "success_hints=%q\n", t.SuccessLines)
	}
	return b.String()
}

// TraceDirFromEnv returns CIE_TRACE_DIR if set (harness / optimizer prompt capture).
func TraceDirFromEnv() string {
	return strings.TrimSpace(os.Getenv("CIE_TRACE_DIR"))
}
