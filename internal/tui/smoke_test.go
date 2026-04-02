package tui

import (
	"strings"
	"testing"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cie-team/cie/internal/backend"
	"github.com/cie-team/cie/internal/config"
)

func TestSmoke_ProgramQuitsOnQ(t *testing.T) {
	cfg := config.Default()
	cfg.Storage.Backend = "memory"
	cfg.Evaluation.DefaultEvaluator = "mock"
	cfg.ExpandPaths()
	b, err := backend.New(cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer b.Close()

	m := New(Options{
		Backend: b,
		Version: "test",
	})
	p := tea.NewProgram(m,
		tea.WithoutRenderer(),
		tea.WithAltScreen(),
		tea.WithInput(strings.NewReader("q")),
	)
	if _, err := p.Run(); err != nil {
		t.Fatal(err)
	}
}
