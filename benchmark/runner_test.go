package benchmark

import (
	"context"
	"testing"
)

func TestRunnerStubPassRate(t *testing.T) {
	r := NewRunner("test")
	tasks := DefaultTasks()
	res, err := r.RunAll(context.Background(), tasks, StubExecutorContext())
	if err != nil {
		t.Fatal(err)
	}
	if len(res) != len(tasks) {
		t.Fatalf("len %d", len(res))
	}
	pr := PassRate(res)
	if pr < 0.5 {
		t.Fatalf("pass rate %v", pr)
	}
}
