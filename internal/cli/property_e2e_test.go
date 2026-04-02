package cli_test

import (
	"bytes"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"testing"

	"github.com/cie-team/cie/internal/cli"
	"github.com/cie-team/cie/internal/config"
	"pgregory.net/rapid"
)

func writeTempJSONConfig(tb testing.TB, experimentsDir string) string {
	tb.Helper()
	cfg := config.Default()
	cfg.Storage.Backend = "json"
	cfg.Storage.ExperimentsDir = experimentsDir
	cfg.Evaluation.DefaultEvaluator = "mock"
	cfg.ExpandPaths()
	p := filepath.Join(experimentsDir, "config.json")
	if err := cfg.Save(p); err != nil {
		tb.Fatal(err)
	}
	return p
}

func runCLI(tb testing.TB, args ...string) (stdout, stderr string, err error) {
	tb.Helper()
	out, errOut := &bytes.Buffer{}, &bytes.Buffer{}
	r := cli.NewRoot()
	r.SetOut(out)
	r.SetErr(errOut)
	r.SetArgs(args)
	err = r.Execute()
	return out.String(), errOut.String(), err
}

func TestProperty_CLI_OptimizeThenStatsTrialCount(t *testing.T) {
	reTrials := regexp.MustCompile(`Trials:\s+(\d+)`)
	rapid.Check(t, func(rt *rapid.T) {
		dir := t.TempDir()
		cfgPath := writeTempJSONConfig(t, dir)
		n := rapid.IntRange(1, 15).Draw(rt, "n")
		opt := rapid.IntRange(0, 1).Draw(rt, "opt")
		wl := rapid.IntRange(0, 4).Draw(rt, "wl")

		_, _, err := runCLI(t, "--config", cfgPath, "optimize",
			"-o", strconv.Itoa(opt), "-w", strconv.Itoa(wl), "-i", strconv.Itoa(n))
		if err != nil {
			rt.Fatal(err)
		}
		out, _, err := runCLI(t, "--config", cfgPath, "stats")
		if err != nil {
			rt.Fatal(err)
		}
		m := reTrials.FindStringSubmatch(out)
		if m == nil {
			rt.Fatalf("could not parse trials from stats: %q", out)
		}
		count, err := strconv.Atoi(m[1])
		if err != nil {
			rt.Fatal(err)
		}
		if count != n {
			rt.Fatalf("stats trial count %d, want %d", count, n)
		}
	})
}

var trialRowRe = regexp.MustCompile(`(?m)^\s*(\d+)\s+\S`)

func TestProperty_CLI_TrialsListsAllRows(t *testing.T) {
	rapid.Check(t, func(rt *rapid.T) {
		dir := t.TempDir()
		cfgPath := writeTempJSONConfig(t, dir)
		n := rapid.IntRange(1, 12).Draw(rt, "n")
		_, _, err := runCLI(t, "--config", cfgPath, "optimize", "-i", strconv.Itoa(n))
		if err != nil {
			rt.Fatal(err)
		}
		out, _, err := runCLI(t, "--config", cfgPath, "trials", "-l", "1000")
		if err != nil {
			rt.Fatal(err)
		}
		seen := map[int]bool{}
		for _, m := range trialRowRe.FindAllStringSubmatch(out, -1) {
			id, err := strconv.Atoi(m[1])
			if err != nil {
				continue
			}
			seen[id] = true
		}
		for i := 1; i <= n; i++ {
			if !seen[i] {
				rt.Fatalf("trial id %d missing from trials output %q", i, out)
			}
		}
	})
}

func TestCLI_HelpDoctorWorkloads(t *testing.T) {
	out, _, err := runCLI(t, "--help")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out, "optimize") {
		t.Fatalf("help missing optimize: %q", out)
	}
	out2, _, err := runCLI(t, "doctor")
	if err != nil {
		t.Fatal(err)
	}
	if len(strings.TrimSpace(out2)) < 8 {
		t.Fatalf("doctor: %q", out2)
	}
	dir := t.TempDir()
	out3, _, err := runCLI(t, "--config", writeTempJSONConfig(t, dir), "workloads")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(out3, "MicroEval") {
		t.Fatalf("workloads: %q", out3)
	}
}
