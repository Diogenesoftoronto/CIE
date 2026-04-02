package benchmark

// Difficulty is task difficulty (ported from Python enum).
type Difficulty string

const (
	Trivial Difficulty = "trivial"
	Easy    Difficulty = "easy"
	Medium  Difficulty = "medium"
	Hard    Difficulty = "hard"
	Expert  Difficulty = "expert"
)

// Category groups tasks by competency.
type Category string

const (
	CatNavigation    Category = "navigation"
	CatComprehension Category = "comprehension"
	CatModification  Category = "modification"
	CatTesting       Category = "testing"
)

// Task is one benchmark unit.
type Task struct {
	ID           string
	Title        string
	Description  string
	Category     Category
	Difficulty   Difficulty
	Objective    string
	SuccessLines []string
	EstMinutes   int
	MaxToolCalls int
	Tags         []string
}
