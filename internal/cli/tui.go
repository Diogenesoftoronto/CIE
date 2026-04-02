package cli

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/cie-team/cie/internal/backend"
	"github.com/cie-team/cie/internal/tui"
)

// Exit writes msg to stderr and exits with code.
func Exit(code int, msg string) {
	if msg != "" {
		fmt.Fprintln(os.Stderr, msg)
	}
	os.Exit(code)
}

// RunTUI starts the Bubble Tea application with a live backend.
func RunTUI(b *backend.Backend, demo bool, scenario string) error {
	m := tui.New(tui.Options{
		Backend:  b,
		DemoMode: demo,
		Scenario: scenario,
		Version:  Version,
	})
	p := tea.NewProgram(m, tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		return fmt.Errorf("tui: %w", err)
	}
	return nil
}
