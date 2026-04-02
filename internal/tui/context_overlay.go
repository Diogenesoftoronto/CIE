package tui

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"

	"github.com/cie-team/cie/internal/backend"
)

func contextToolsOverlay(w, h int, opts Options, bk *backend.Backend) string {
	if w < 40 {
		w = 40
	}
	bodyW := w - 6
	if bodyW > 78 {
		bodyW = 78
	}
	if bodyW < 20 {
		bodyW = 20
	}

	var b strings.Builder
	b.WriteString("Context tools\n\n")
	b.WriteString("Keyboard:\n")
	b.WriteString("  ctrl+/    Open or close this sheet\n")
	b.WriteString("  esc       Close\n")
	b.WriteString("  ctrl+r    Reload trials from storage\n")
	b.WriteString("  tab       Next panel\n\n")
	b.WriteString("W&B import:\n")
	b.WriteString("  cie wandb sync [run-dir]\n")
	b.WriteString("  env CIE_WANDB_RUN=/path/to/run\n\n")
	b.WriteString("Benchmark harness:\n")
	b.WriteString("  cie benchmark run\n\n")
	if bk != nil {
		s := bk.Stats()
		b.WriteString("Live backend:\n")
		fmt.Fprintf(&b, "  %v trials · storage %v · eval %v\n", s["trial_count"], s["storage_type"], s["evaluator"])
	} else {
		b.WriteString("No backend attached.\n")
	}
	if opts.DemoMode {
		fmt.Fprintf(&b, "\nDemo scenario: %s\n", opts.Scenario)
	}

	text := wordWrap(strings.TrimSpace(b.String()), bodyW)
	box := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("205")).
		Padding(1, 2).
		Width(bodyW + 4).
		Background(lipgloss.Color("236")).
		Foreground(lipgloss.Color("252")).
		Render(text)
	title := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("81")).Render("[ Context tools ]")
	return lipgloss.JoinVertical(lipgloss.Left, title, box)
}
