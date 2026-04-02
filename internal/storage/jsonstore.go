package storage

import (
	"cmp"
	"encoding/json"
	"os"
	"path/filepath"
	"slices"

	"github.com/cie-team/cie/internal/core"
)

// JSON stores trials/policies/prompts as JSON files under a directory.
type JSON struct {
	dir          string
	trialsFile   string
	policiesFile string
	promptsFile  string
}

// NewJSON creates a JSON file backend under dir.
func NewJSON(dir string) (*JSON, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, err
	}
	return &JSON{
		dir:          dir,
		trialsFile:   filepath.Join(dir, "trials.json"),
		policiesFile: filepath.Join(dir, "policies.json"),
		promptsFile:  filepath.Join(dir, "prompts.json"),
	}, nil
}

func (j *JSON) load(path string, out any) error {
	b, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	return json.Unmarshal(b, out)
}

func (j *JSON) save(path string, v any) error {
	b, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o644)
}

func (j *JSON) SaveTrial(t *core.Trial) error {
	var trials []core.Trial
	if err := j.load(j.trialsFile, &trials); err != nil {
		return err
	}
	trials = append(trials, *t)
	return j.save(j.trialsFile, trials)
}

func (j *JSON) GetTrials(limit int) ([]core.Trial, error) {
	var trials []core.Trial
	if err := j.load(j.trialsFile, &trials); err != nil {
		return nil, err
	}
	slices.SortFunc(trials, func(a, b core.Trial) int {
		return cmp.Compare(b.CreatedAt.UnixNano(), a.CreatedAt.UnixNano())
	})
	if limit > 0 && len(trials) > limit {
		trials = trials[:limit]
	}
	return trials, nil
}

func (j *JSON) SavePolicy(p *core.Policy) error {
	var policies []core.Policy
	_ = j.load(j.policiesFile, &policies)
	out := policies[:0]
	for _, x := range policies {
		if x.Name != p.Name {
			out = append(out, x)
		}
	}
	out = append(out, *p)
	return j.save(j.policiesFile, out)
}

func (j *JSON) GetPolicies() ([]core.Policy, error) {
	var policies []core.Policy
	if err := j.load(j.policiesFile, &policies); err != nil {
		return nil, err
	}
	return policies, nil
}

func (j *JSON) SavePrompt(p *core.Prompt) error {
	var prompts []core.Prompt
	_ = j.load(j.promptsFile, &prompts)
	out := prompts[:0]
	for _, x := range prompts {
		if x.ID != p.ID {
			out = append(out, x)
		}
	}
	out = append(out, *p)
	return j.save(j.promptsFile, out)
}

func (j *JSON) GetPrompts() ([]core.Prompt, error) {
	var prompts []core.Prompt
	if err := j.load(j.promptsFile, &prompts); err != nil {
		return nil, err
	}
	return prompts, nil
}

func (j *JSON) DeletePrompt(id string) error {
	prompts, err := j.GetPrompts()
	if err != nil {
		return err
	}
	out := prompts[:0]
	for _, x := range prompts {
		if x.ID != id {
			out = append(out, x)
		}
	}
	return j.save(j.promptsFile, out)
}

func (j *JSON) ClearAll() error {
	_ = os.Remove(j.trialsFile)
	_ = os.Remove(j.policiesFile)
	_ = os.Remove(j.promptsFile)
	return nil
}

func (j *JSON) Close() error { return nil }
