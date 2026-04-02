package llm

import (
	"context"
	"strings"

	"github.com/maruel/genai"
)

// ChatText runs a single user turn with optional system prompt via GenSync.
func ChatText(ctx context.Context, p genai.Provider, registryKey, system, user string, temperature float64, maxTokens int64) (genai.Result, error) {
	msgs := genai.Messages{genai.NewTextMessage(user)}
	opt := &genai.GenOptionText{
		Temperature:  temperature,
		MaxTokens:    maxTokens,
		SystemPrompt: system,
		ReplyAsJSON:  UseJSONMode(registryKey),
		TopP:         1,
	}
	return p.GenSync(ctx, msgs, opt)
}

// ResultText concatenates assistant text blocks from a genai Result.
func ResultText(r genai.Result) string {
	var b strings.Builder
	for i := range r.Replies {
		b.WriteString(r.Replies[i].Text)
	}
	return b.String()
}
