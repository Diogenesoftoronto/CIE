package optimizer

import (
	"fmt"
	"math/rand/v2"
	"time"

	"github.com/cie-team/cie/internal/core"
)

// RandomProbe proposes uniformly random parameters (baseline explorer).
type RandomProbe struct {
	rng    *rand.Rand
	ranges map[string]paramRange
	step   int
}

// NewRandomProbe builds a random optimizer.
func NewRandomProbe() *RandomProbe {
	src := rand.NewPCG(uint64(time.Now().UnixNano())^0xcafebabe, 1)
	return &RandomProbe{
		rng:    rand.New(src),
		ranges: defaultRanges(),
	}
}

func (r *RandomProbe) Name() string { return "RandomProbe" }

func (r *RandomProbe) Reset() { r.step = 0 }

func (r *RandomProbe) GetState() map[string]any {
	return map[string]any{"iteration": r.step}
}

func (r *RandomProbe) Propose(_ map[string]any) *core.Policy {
	r.step++
	p := randomParams(r.rng, r.ranges)
	p["artifact"] = fmt.Sprintf("random-%d-%d", time.Now().UnixMilli(), r.step)
	p["iteration"] = float64(r.step)
	return &core.Policy{
		Name:      r.Name(),
		Params:    p,
		Actions:   actionsFromParams(p),
		CreatedAt: time.Now().UTC(),
		Metadata:  map[string]any{"optimizer": r.Name()},
	}
}

func (r *RandomProbe) Observe(_ *core.Policy, _ map[string]float64) {}
