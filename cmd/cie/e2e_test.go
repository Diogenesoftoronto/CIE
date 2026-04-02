package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"testing"

	"github.com/cie-team/cie/internal/config"
	"pgregory.net/rapid"
)

func repoRoot(t *testing.T) string {
	t.Helper()
	wd, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	for d := wd; ; d = filepath.Dir(d) {
		if st, err := os.Stat(filepath.Join(d, "go.mod")); err == nil && !st.IsDir() {
			return d
		}
		if filepath.Dir(d) == d {
			break
		}
	}
	t.Fatalf("go.mod not found from %s", wd)
	return ""
}

func buildCIE(tb testing.TB, root, bin string) {
	tb.Helper()
	cmd := exec.Command("go", "build", "-o", bin, "./cmd/cie")
	cmd.Dir = root
	out, err := cmd.CombinedOutput()
	if err != nil {
		tb.Fatalf("go build: %v\n%s", err, out)
	}
}

func TestBinary_HelpAndDoctor(t *testing.T) {
	root := repoRoot(t)
	bin := filepath.Join(t.TempDir(), "cie")
	buildCIE(t, root, bin)

	cmd := exec.Command(bin, "--help")
	out, err := cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("--help: %v\n%s", err, out)
	}
	cmd = exec.Command(bin, "doctor")
	out, err = cmd.CombinedOutput()
	if err != nil {
		t.Fatalf("doctor: %v\n%s", err, out)
	}
}

var statsTrialsRe = regexp.MustCompile(`Trials:\s+(\d+)`)

func TestProperty_Binary_OptimizeStatsMatch(t *testing.T) {
	root := repoRoot(t)
	bin := filepath.Join(t.TempDir(), "cie")
	buildCIE(t, root, bin)

	rapid.Check(t, func(rt *rapid.T) {
		dir, err := os.MkdirTemp("", "cie-e2e-*")
		if err != nil {
			rt.Fatal(err)
		}
		defer func() { _ = os.RemoveAll(dir) }()

		cfg := config.Default()
		cfg.Storage.Backend = "json"
		cfg.Storage.ExperimentsDir = dir
		cfg.Evaluation.DefaultEvaluator = "mock"
		cfg.ExpandPaths()
		cfgPath := filepath.Join(dir, "config.json")
		if err := cfg.Save(cfgPath); err != nil {
			rt.Fatal(err)
		}

		n := rapid.IntRange(1, 12).Draw(rt, "n")
		opt := rapid.IntRange(0, 1).Draw(rt, "opt")
		wl := rapid.IntRange(0, 4).Draw(rt, "wl")

		cmd := exec.Command(bin, "--config", cfgPath, "optimize",
			"-o", strconv.Itoa(opt), "-w", strconv.Itoa(wl), "-i", strconv.Itoa(n))
		cmd.Dir = root
		out, err := cmd.CombinedOutput()
		if err != nil {
			rt.Fatalf("optimize: %v\n%s", err, out)
		}
		cmd = exec.Command(bin, "--config", cfgPath, "stats")
		cmd.Dir = root
		out, err = cmd.CombinedOutput()
		if err != nil {
			rt.Fatalf("stats: %v\n%s", err, out)
		}
		m := statsTrialsRe.FindSubmatch(out)
		if m == nil {
			rt.Fatalf("stats missing Trials line: %s", out)
		}
		got, err := strconv.Atoi(string(m[1]))
		if err != nil {
			rt.Fatal(err)
		}
		if got != n {
			rt.Fatalf("stats trials %d want %d", got, n)
		}
	})
}
