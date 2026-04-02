package evaluator

import "fmt"

// ErrUnknown indicates an unregistered evaluator slug.
type ErrUnknown string

func (e ErrUnknown) Error() string {
	return fmt.Sprintf("unknown evaluator %q", string(e))
}
