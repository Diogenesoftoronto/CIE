package tui

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/cie-team/cie/internal/backend"
)

// Panel id matches Python TUI sidebar concepts.
type Panel string

const (
	PanelOptimizers  Panel = "optimizers"
	PanelEvals       Panel = "evals"
	PanelExperiments Panel = "experiments"
	PanelPrompts     Panel = "prompts"
	PanelContext     Panel = "context"
	PanelStatus      Panel = "status"
)

var panelOrder = []Panel{
	PanelOptimizers,
	PanelEvals,
	PanelExperiments,
	PanelPrompts,
	PanelContext,
	PanelStatus,
}

var panelTitles = map[Panel]string{
	PanelOptimizers:  "Optimizers",
	PanelEvals:       "Evaluations",
	PanelExperiments: "Experiments",
	PanelPrompts:     "Prompts",
	PanelContext:     "Context",
	PanelStatus:      "Status",
}

// Options configures the Bubble Tea program.
type Options struct {
	Backend  *backend.Backend
	DemoMode bool
	Scenario string
	Version  string
}

// Model is the root TUI state (Crush-style layered shell: chrome + focus panes).
type Model struct {
	opts         Options
	backend      *backend.Backend
	width        int
	height       int
	sidebarWidth int

	sidebar list.Model
	active  Panel

	statusLine string

	// contextTools is a lightweight modal (ported from Python ContextToolsModal).
	showContext bool
}

// New builds the initial model.
func New(opts Options) Model {
	items := make([]list.Item, 0, len(panelOrder))
	for _, p := range panelOrder {
		items = append(items, panelItem{id: p})
	}

	delegate := list.NewDefaultDelegate()
	delegate.Styles.SelectedTitle = delegate.Styles.SelectedTitle.Foreground(lipgloss.Color("205")).Bold(true)
	delegate.Styles.SelectedDesc = delegate.Styles.SelectedDesc.Foreground(lipgloss.Color("244"))

	l := list.New(items, delegate, 0, 0)
	l.Title = "Panels"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.DisableQuitKeybindings()
	l.Styles.Title = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("81"))

	m := Model{
		opts:       opts,
		backend:    opts.Backend,
		sidebar:    l,
		active:     PanelOptimizers,
		statusLine: "ctrl+r refresh · ctrl+/ context · tab panel · q quit",
	}
	return m
}

type panelItem struct {
	id Panel
}

func (p panelItem) Title() string       { return panelTitles[p.id] }
func (p panelItem) Description() string { return "" }
func (p panelItem) FilterValue() string { return panelTitles[p.id] }

// Init implements tea.Model.
func (m Model) Init() tea.Cmd {
	return nil
}

// Update implements tea.Model.
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	if m.showContext {
		if km, ok := msg.(tea.KeyMsg); ok {
			switch km.String() {
			case "esc", "ctrl+/", "enter":
				m.showContext = false
				return m, nil
			}
		}
		return m, nil
	}

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "tab":
			m.focusNext()
			m.syncSidebarSelection()
			return m, nil
		case "shift+tab":
			m.focusPrev()
			m.syncSidebarSelection()
			return m, nil
		case "ctrl+r":
			if m.backend != nil {
				_ = m.backend.Reload()
			}
			return m, nil
		case "ctrl+/":
			m.showContext = true
			return m, nil
		}
	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		topBar := 3
		statusBar := 1
		sidebarW := clamp(msg.Width/5, 22, 36)
		m.sidebarWidth = sidebarW
		listH := msg.Height - topBar - statusBar
		m.sidebar.SetSize(sidebarW, max(listH, 6))
		return m, nil
	}

	var cmd tea.Cmd
	m.sidebar, cmd = m.sidebar.Update(msg)
	if sel, ok := m.sidebar.SelectedItem().(panelItem); ok {
		m.active = sel.id
	}
	return m, cmd
}

// View implements tea.Model.
func (m Model) View() string {
	if m.width == 0 {
		return "Loading…"
	}

	v := m.opts.Version
	if v == "" {
		v = "dev"
	}
	mode := ""
	if m.opts.DemoMode {
		mode = lipgloss.NewStyle().Foreground(lipgloss.Color("214")).Bold(true).Render(
			fmt.Sprintf(" demo · %s ", m.opts.Scenario),
		)
	}

	top := lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("15")).
		Background(lipgloss.Color("57")).
		Padding(0, 1).
		Width(m.width).
		Render(" CIE · Optimization & Evaluation " + mode + lipgloss.NewStyle().Foreground(lipgloss.Color("252")).Render("  v"+v))

	contentW := m.width - m.sidebarWidth - 4
	if contentW < 20 {
		contentW = 20
	}
	body := m.renderMain(contentW)

	row := lipgloss.JoinHorizontal(
		lipgloss.Top,
		m.sidebar.View(),
		lipgloss.NewStyle().MarginLeft(1).Width(contentW).Render(body),
	)

	status := lipgloss.NewStyle().
		Foreground(lipgloss.Color("241")).
		Width(m.width).
		Render(m.statusLine)

	base := lipgloss.JoinVertical(lipgloss.Left, top, row, status)
	if !m.showContext {
		return base
	}
	ov := contextToolsOverlay(m.width, m.height, m.opts, m.backend)
	return lipgloss.Place(m.width, m.height, lipgloss.Center, lipgloss.Center, ov)
}

func (m *Model) focusNext() {
	for i, p := range panelOrder {
		if p == m.active {
			m.active = panelOrder[(i+1)%len(panelOrder)]
			return
		}
	}
	m.active = panelOrder[0]
}

func (m *Model) focusPrev() {
	for i, p := range panelOrder {
		if p == m.active {
			m.active = panelOrder[(i-1+len(panelOrder))%len(panelOrder)]
			return
		}
	}
	m.active = panelOrder[0]
}

func (m *Model) syncSidebarSelection() {
	for i, it := range m.sidebar.Items() {
		pi, ok := it.(panelItem)
		if !ok {
			continue
		}
		if pi.id == m.active {
			m.sidebar.Select(i)
			return
		}
	}
}

func (m Model) renderMain(width int) string {
	title := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("86")).Render(panelTitles[m.active])
	blurb := placeholderCopy(m.active, m.opts, m.backend)
	box := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("238")).
		Padding(1, 1).
		Width(width).
		Render(title + "\n\n" + blurb)
	return box
}

func placeholderCopy(p Panel, opts Options, bk *backend.Backend) string {
	switch p {
	case PanelOptimizers:
		return wordWrap(
			"Optimizers: HillClimb, RandomProbe, and OpenAI:PolicyJSON (chat JSON when API key + provider are set). "+
				"`cie optimizers` lists indices.",
			76,
		)
	case PanelEvals:
		return wordWrap(
			"Evaluators: `mock` (synthetic metrics) and `text-match` (Levenshtein on embedded cases). "+
				"Switch with `cie evaluators --use <slug>`.",
			76,
		)
	case PanelExperiments:
		if bk != nil && len(bk.Trials) > 0 {
			n := len(bk.Trials)
			pn := len(bk.Pareto)
			return wordWrap(fmt.Sprintf("%d trials loaded, %d Pareto points. CLI: `cie trials --pareto`.", n, pn), 76)
		}
		return wordWrap(
			"No trials yet. Run `cie optimize --iterations 5` then press ctrl+r to refresh counts.",
			76,
		)
	case PanelPrompts:
		return wordWrap("Prompt templates: managed via storage API (coming to this panel).", 76)
	case PanelContext:
		return wordWrap(
			"Press ctrl+/ for the context-tools sheet (snapshot, W&B sync hints, keyboard reference). "+
				"CLI: `cie wandb sync` imports a local run; `cie benchmark run` runs the harness.",
			76,
		)
	case PanelStatus:
		if bk != nil {
			s := bk.Stats()
			msg := fmt.Sprintf(
				"storage=%v trials=%v pareto=%v eval=%v optimizers=%v active_policy=%v",
				s["storage_type"], s["trial_count"], s["pareto_count"], s["evaluator"],
				s["optimizer_count"], s["active_policy"],
			)
			if opts.DemoMode {
				msg = "demo · " + opts.Scenario + " · " + msg
			}
			return wordWrap(msg, 76)
		}
		if opts.DemoMode {
			return wordWrap("Demo mode ("+opts.Scenario+") - backend not wired.", 76)
		}
		return wordWrap("No backend attached.", 76)
	default:
		return ""
	}
}

func wordWrap(s string, lineLen int) string {
	if lineLen <= 0 {
		return s
	}
	words := strings.Fields(s)
	var b strings.Builder
	line := 0
	for _, w := range words {
		if line == 0 {
			b.WriteString(w)
			line = len(w)
			continue
		}
		if line+1+len(w) > lineLen {
			b.WriteByte('\n')
			b.WriteString(w)
			line = len(w)
		} else {
			b.WriteByte(' ')
			b.WriteString(w)
			line += 1 + len(w)
		}
	}
	return b.String()
}

func clamp(n, low, high int) int {
	if n < low {
		return low
	}
	if n > high {
		return high
	}
	return n
}
