import React, { useState } from 'react'
import { Brain, TrendingUp, Shuffle, Settings, Code, Zap } from 'lucide-react'

const Algorithms: React.FC = () => {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('dspy')

  const algorithms = [
    {
      id: 'dspy',
      name: 'DSPy Optimization',
      icon: Brain,
      color: 'blue',
      description: 'AI-powered optimization using DSPy with artifact management and k-shot learning',
      features: [
        'Automated prompt optimization',
        'Artifact-based policy generation',
        'K-shot learning with examples',
        'Multi-model support (OpenAI, Kimi)'
      ],
      pros: ['High-quality results', 'Automated prompt engineering', 'Multi-model support'],
      cons: ['Requires API keys', 'Higher computational cost', 'Model-dependent performance'],
      code: `class DspyOptimizer:
    def propose(self, state: Dict[str, Any]) -> Policy:
        # Generate artifacts based on current state
        artifacts = self.dspy_generator(
            examples=state.get('examples', []),
            metrics=state.get('metrics', {})
        )
        
        return Policy(
            parameters={
                'prompt_template': artifacts.prompt,
                'k_shot_examples': artifacts.examples,
                'model_config': artifacts.config
            },
            metadata={'algorithm': 'dspy', 'iteration': state.get('iteration', 0)}
        )`
    },
    {
      id: 'hillclimb',
      name: 'Hill Climbing',
      icon: TrendingUp,
      color: 'green',
      description: 'Gradient-based optimization with random restarts and adaptive step sizes',
      features: [
        'Random parameter exploration',
        'Adaptive step size adjustment',
        'Local optimum detection',
        'Multiple restart strategies'
      ],
      pros: ['Simple and fast', 'No gradients required', 'Good local optimization'],
      cons: ['Can get stuck in local optima', 'Limited exploration', 'Sensitive to initial conditions'],
      code: `class HillClimbOptimizer:
    def propose(self, state: Dict[str, Any]) -> Policy:
        current_params = state.get('current_params', {})
        step_size = state.get('step_size', 0.1)
        
        # Generate neighbor solution
        new_params = {}
        for key, value in current_params.items():
            perturbation = np.random.uniform(-step_size, step_size)
            new_params[key] = np.clip(value + perturbation, 0, 1)
        
        return Policy(
            parameters=new_params,
            metadata={'algorithm': 'hillclimb', 'step_size': step_size}
        )`
    },
    {
      id: 'bandit',
      name: 'Multi-Armed Bandit',
      icon: Shuffle,
      color: 'purple',
      description: 'Exploration-exploitation trade-off with Thompson sampling and UCB',
      features: [
        'Thompson sampling',
        'Upper Confidence Bound (UCB)',
        'Bayesian reward estimation',
        'Contextual bandit support'
      ],
      pros: ['Good exploration-exploitation balance', 'Theoretical guarantees', 'Online learning'],
      cons: ['Requires reward feedback', 'Can be slow to converge', 'Complex implementation'],
      code: `class BanditOptimizer:
    def __init__(self, n_arms: int = 5):
        self.n_arms = n_arms
        self.counts = [0] * n_arms
        self.values = [0.0] * n_arms
        
    def propose(self, state: Dict[str, Any]) -> Policy:
        # UCB algorithm for arm selection
        ucb_values = []
        total_counts = sum(self.counts)
        
        for i in range(self.n_arms):
            if self.counts[i] == 0:
                ucb_values.append(float('inf'))
            else:
                bonus = sqrt(2 * log(total_counts) / self.counts[i])
                ucb_values.append(self.values[i] + bonus)
        
        selected_arm = np.argmax(ucb_values)
        
        return Policy(
            parameters={'selected_arm': selected_arm},
            metadata={'algorithm': 'bandit', 'arm': selected_arm}
        )`
    }
  ]

  const currentAlgorithm = algorithms.find(a => a.id === selectedAlgorithm)

  return (
    <section id="algorithms" className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Optimization Algorithms
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Three complementary optimization strategies, each designed for different scenarios and 
            requirements. Choose the right algorithm based on your specific needs and constraints.
          </p>
        </div>

        {/* Algorithm Selector */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex bg-slate-100 rounded-lg p-1">
            {algorithms.map((algorithm) => {
              const Icon = algorithm.icon
              return (
                <button
                  key={algorithm.id}
                  onClick={() => setSelectedAlgorithm(algorithm.id)}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-md transition-all duration-200 ${
                    selectedAlgorithm === algorithm.id
                      ? `bg-white shadow-sm text-${algorithm.color}-600`
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{algorithm.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Algorithm Details */}
        {currentAlgorithm && (
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Left Column - Overview */}
            <div className="space-y-8">
              <div className="distill-card rounded-xl p-8">
                <div className="flex items-center mb-6">
                  <div className={`w-12 h-12 bg-${currentAlgorithm.color}-100 rounded-lg flex items-center justify-center mr-4`}>
                    <currentAlgorithm.icon className={`w-6 h-6 text-${currentAlgorithm.color}-600`} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-slate-900">{currentAlgorithm.name}</h3>
                    <p className="text-slate-600">{currentAlgorithm.description}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-lg font-medium text-slate-800">Key Features</h4>
                  <div className="grid grid-cols-1 gap-3">
                    {currentAlgorithm.features.map((feature, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`w-2 h-2 bg-${currentAlgorithm.color}-500 rounded-full mt-2 flex-shrink-0`} />
                        <span className="text-slate-600">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="distill-card rounded-xl p-6">
                  <h4 className="text-lg font-medium text-slate-800 mb-4 flex items-center">
                    <Zap className="w-5 h-5 text-green-600 mr-2" />
                    Strengths
                  </h4>
                  <ul className="space-y-2">
                    {currentAlgorithm.pros.map((pro, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm text-slate-600">{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="distill-card rounded-xl p-6">
                  <h4 className="text-lg font-medium text-slate-800 mb-4 flex items-center">
                    <Settings className="w-5 h-5 text-orange-600 mr-2" />
                    Considerations
                  </h4>
                  <ul className="space-y-2">
                    {currentAlgorithm.cons.map((con, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm text-slate-600">{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Right Column - Code */}
            <div>
              <div className="distill-card rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-medium text-slate-800">Implementation</h4>
                  <Code className="w-5 h-5 text-slate-400" />
                </div>
                <div className="code-block">
                  <pre className="text-sm">{currentAlgorithm.code}</pre>
                </div>
              </div>

              <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
                <h4 className="text-lg font-medium text-slate-800 mb-4">When to Use</h4>
                <div className="space-y-3 text-slate-600">
                  {selectedAlgorithm === 'dspy' && (
                    <>
                      <p>• You have access to powerful language models</p>
                      <p>• Prompt optimization is critical for performance</p>
                      <p>• You need high-quality, automated solutions</p>
                      <p>• Budget allows for API costs</p>
                    </>
                  )}
                  {selectedAlgorithm === 'hillclimb' && (
                    <>
                      <p>• You have continuous parameter spaces</p>
                      <p>• Local optimization is sufficient</p>
                      <p>• You need fast, simple optimization</p>
                      <p>• Gradient information is unavailable</p>
                    </>
                  )}
                  {selectedAlgorithm === 'bandit' && (
                    <>
                      <p>• You have discrete choices to explore</p>
                      <p>• Online learning is required</p>
                      <p>• Exploration-exploitation trade-off matters</p>
                      <p>• You can get immediate feedback</p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default Algorithms