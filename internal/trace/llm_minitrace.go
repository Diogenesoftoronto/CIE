package trace

import (
	"fmt"
	"strings"

	"github.com/cie-team/cie/internal/config"
	"github.com/cie-team/cie/internal/llm"
	"github.com/go-go-golems/go-minitrace/pkg/minitrace"
	"github.com/google/uuid"
	"github.com/maruel/genai"
)

// WriteLLMSession writes one system/user/assistant exchange as a minitrace session file under dir
// (same layout as go-minitrace: active/YYYY-MM/<id>.minitrace.json). Empty dir is a no-op.
func WriteLLMSession(dir, op string, cfg *config.Config, registryKey, system, user string, res genai.Result) error {
	dir = strings.TrimSpace(dir)
	if dir == "" {
		return nil
	}
	sid := uuid.NewString()
	s := minitrace.BuildSessionSkeleton(sid, "cie", "cie-harness", "cie/llm-trace")
	if op != "" {
		s.Title = minitracePtr(op)
	}
	if cfg != nil {
		mn := strings.TrimSpace(cfg.Model.ModelName)
		if mn != "" {
			s.Environment.Model = minitracePtr(mn)
		}
		if t := cfg.Model.Temperature; t != 0 {
			s.Environment.Temperature = minitracePtr(t)
		}
	}
	if registryKey != "" {
		s.Environment.ProviderHint = minitracePtr(registryKey)
	}
	now := minitrace.FormatTimestamp(minitrace.NowUTC())
	s.Timing.StartedAt = minitracePtr(now)
	s.Timing.EndedAt = minitracePtr(now)

	s.Turns = append(s.Turns,
		minitrace.BuildTurn(0, minitracePtr(now), "system", minitracePtr("cie"), system),
		minitrace.BuildTurn(1, minitracePtr(now), "user", minitracePtr("cie"), user),
		minitrace.BuildTurn(2, minitracePtr(now), "assistant", minitracePtr(registryKey), llm.ResultText(res)),
	)
	if res.Usage.TotalTokens > 0 || res.Usage.OutputTokens > 0 {
		it := int(res.Usage.InputTokens)
		ot := int(res.Usage.OutputTokens)
		s.Turns[2].Usage = &minitrace.Usage{InputTokens: minitracePtr(it), OutputTokens: minitracePtr(ot)}
	}
	_, err := minitrace.WriteSession(&s, dir)
	if err != nil {
		return fmt.Errorf("minitrace write: %w", err)
	}
	return nil
}

func minitracePtr[T any](v T) *T { return &v }
