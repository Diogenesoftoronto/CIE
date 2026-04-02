import React, { useState } from 'react'
import { Database, Cpu, Settings, Eye, Brain } from 'lucide-react'

const Architecture: React.FC = () => {
  const [selectedLayer, setSelectedLayer] = useState<string>('backend')

  const layers = [
    {
      id: 'ui',
      name: 'User Interface',
      icon: Eye,
      color: 'blue',
      description: 'Interactive TUI and web interface for experiment management',
      details: [
        'React-based web interface with shadcn/ui components',
        'Textual TUI with Harlequin-inspired sidebar layout',
        'Prompts Panel for DSPy signature management',
        'Real-time updates and interactive visualizations',
        'Responsive design with mobile support'
      ]
    },
    {
      id: 'context',
      name: 'Context Introspection',
      icon: Brain,
      color: 'indigo',
      description: 'Advanced context analysis and manipulation system',
      details: [
        'Real-time context window usage monitoring',
        'Hierarchical context tree visualization',
        'Context compression and optimization algorithms',
        'Access pattern analysis and hotspot detection'
      ]
    },
    {
      id: 'backend',
      name: 'Backend Core',
      icon: Cpu,
      color: 'purple',
      description: 'Central orchestration and state management',
      details: [
        'Protocol-based storage backends (SQLite, JSON, Memory)',
        'Multi-dimensional scoring with Pareto frontier optimization',
        'Real-time statistics and monitoring',
        'Guardrails for policy adoption and safety'
      ]
    },
    {
      id: 'algorithms',
      name: 'Optimization Layer',
      icon: Settings,
      color: 'green',
      description: 'AI-powered optimization algorithms',
      details: [
        'DSPy integration with artifact management',
        'Context-aware optimizers with introspection capabilities',
        'Hill climbing and evolutionary algorithms',
        'Custom algorithm support via protocols'
      ]
    },
    {
      id: 'storage',
      name: 'Data Layer',
      icon: Database,
      color: 'orange',
      description: 'Flexible storage and persistence',
      details: [
        'Multiple backend options (SQLite, JSON, In-memory)',
        'Trial history and experiment tracking',
        'Policy versioning and rollback support',
        'Export/import functionality for experiments'
      ]
    }
  ]

  const selectedLayerData = layers.find(layer => layer.id === selectedLayer)

  return (
    <section id="architecture" className="py-20 bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            System Architecture
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            A modular, protocol-based architecture that separates concerns while maintaining
            flexibility and extensibility. Built with modern Python practices and comprehensive
            type safety.
          </p>
        </div>

        {/* Architecture Diagram */}
        <div className="mb-16">
          <div className="bg-white rounded-2xl p-8 shadow-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              {layers.map((layer) => {
                const Icon = layer.icon
                return (
                  <div
                    key={layer.id}
                    className={`p-6 rounded-xl border-2 cursor-pointer transition-all duration-200 distill-hover ${selectedLayer === layer.id
                        ? `border-${layer.color}-500 bg-${layer.color}-50`
                        : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    onClick={() => setSelectedLayer(layer.id)}
                  >
                    <div className={`w-12 h-12 bg-${layer.color}-100 rounded-lg flex items-center justify-center mb-4`}>
                      <Icon className={`w-6 h-6 text-${layer.color}-600`} />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">{layer.name}</h3>
                    <p className="text-sm text-slate-600">{layer.description}</p>
                  </div>
                )
              })}
            </div>

            {/* Connection lines */}
            <div className="mt-8 flex justify-center">
              <div className="flex items-center space-x-4 text-slate-400">
                <div className="w-8 h-0.5 bg-slate-300"></div>
                <span className="text-sm">Protocol-based communication with context introspection</span>
                <div className="w-8 h-0.5 bg-slate-300"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed View */}
        {selectedLayerData && (
          <div className="bg-white rounded-2xl p-8 shadow-lg">
            <div className="flex items-center mb-6">
              <div className={`w-12 h-12 bg-${selectedLayerData.color}-100 rounded-lg flex items-center justify-center mr-4`}>
                <selectedLayerData.icon className={`w-6 h-6 text-${selectedLayerData.color}-600`} />
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-slate-900">{selectedLayerData.name}</h3>
                <p className="text-slate-600">{selectedLayerData.description}</p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-medium text-slate-800 mb-4">Key Features</h4>
                <ul className="space-y-3">
                  {selectedLayerData.details.map((detail, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <div className={`w-2 h-2 bg-${selectedLayerData.color}-500 rounded-full mt-2 flex-shrink-0`} />
                      <span className="text-slate-600">{detail}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="bg-slate-50 rounded-lg p-6">
                <h4 className="text-lg font-medium text-slate-800 mb-4">Code Example</h4>
                <div className="code-block">
                  {selectedLayer === 'backend' && (
                    <pre>{`class CIEBackend:
    def __init__(self, config: CIEConfig):
        self.storage = self._create_storage()
        self.scoring = MultiDimensionalScoring()
        self.pareto = ParetoFrontier()
        
    def optimize(self, policy: Policy) -> Trial:
        # Multi-objective optimization
        score = self.scoring.score(policy.metrics)
        return Trial(policy=policy, score=score)`}</pre>
                  )}
                  {selectedLayer === 'context' && (
                    <pre>{`class AgentContextTools:
    def inspect_context(self, path: str) -> Dict:
        # Analyze context structure and efficiency
        analysis = self.introspector.analyze(path)
        return {
            'efficiency_score': analysis.efficiency,
            'hotspots': analysis.hotspots,
            'optimization_potential': analysis.potential
        }
        
    def compress_context(self, strategy: str) -> Dict:
        # Apply compression algorithms
        return self.manipulator.compress(strategy)`}</pre>
                  )}
                  {selectedLayer === 'algorithms' && (
                    <pre>{`class ContextAwareOptimizer:
    def propose(self, state: Dict) -> Policy:
        # AI-powered optimization with context analysis
        context_analysis = self.context_tools.analyze_context()
        state['context_efficiency'] = context_analysis['efficiency_score']
        
        artifacts = self.generate_artifacts(state)
        return Policy(
            parameters=artifacts,
            metadata={'algorithm': 'context-aware'}
        )`}</pre>
                  )}
                  {selectedLayer === 'ui' && (
                    <pre>{`const OptimizersPanel = () => {
    const [selectedOptimizer, setOptimizer] = useState(null)
    
    return (
        <Card>
            <OptimizerSelector 
                onSelect={setOptimizer}
                algorithms={['DSPy', 'HillClimb', 'ContextAware']}
            />
        </Card>
    )
}`}</pre>
                  )}
                  {selectedLayer === 'storage' && (
                    <pre>{`class SQLiteBackend:
    def store_trial(self, trial: Trial) -> Trial:
        with self.db.transaction():
            trial_id = self.db.execute(
                "INSERT INTO trials (policy, metrics, score) VALUES (?, ?, ?) RETURNING id",
                (trial.policy.json(), trial.metrics.json(), trial.score)
            ).fetchone()[0]
            return trial.with_id(trial_id)`}</pre>
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

export default Architecture