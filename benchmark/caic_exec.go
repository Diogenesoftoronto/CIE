package benchmark

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// CaicExecutor shells out to the caic binary (Coding Agents in Containers, https://github.com/caic-xyz/caic).
// Intended for v0.5.x+. Pass bin from CIE_CAIC_BIN or PATH; extraArgs are appended after default args.
//
// The process receives task metadata in the environment: CIE_TASK_ID, CIE_TASK_TITLE, CIE_TASK_OBJECTIVE.
// A custom caic entrypoint can read these; the default binary may ignore them until wired in your install.
func CaicExecutor(bin string, extraArgs []string) Executor {
	return func(ctx context.Context, t Task) (bool, string, []string) {
		path := strings.TrimSpace(bin)
		if path == "" {
			path = strings.TrimSpace(os.Getenv("CIE_CAIC_BIN"))
		}
		if path == "" {
			if p, err := exec.LookPath("caic"); err == nil {
				path = p
			}
		}
		if path == "" {
			return false, "", []string{
				"caic not found: install from https://github.com/caic-xyz/caic/releases (v0.5.5+) or set CIE_CAIC_BIN",
			}
		}
		args := []string{}
		if len(extraArgs) > 0 {
			args = append(args, extraArgs...)
		}
		cmd := exec.CommandContext(ctx, path, args...)
		cmd.Env = append(os.Environ(),
			"CIE_TASK_ID="+t.ID,
			"CIE_TASK_TITLE="+t.Title,
			"CIE_TASK_OBJECTIVE="+t.Objective,
			"CIE_TASK_DESCRIPTION="+t.Description,
		)
		out, err := cmd.CombinedOutput()
		s := strings.TrimSpace(string(out))
		if err != nil {
			return false, s, []string{fmt.Sprintf("caic: %v", err)}
		}
		return true, s, nil
	}
}
