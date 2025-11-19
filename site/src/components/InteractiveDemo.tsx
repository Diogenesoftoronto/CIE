import React, { useState, useEffect } from 'react'
import { Play, Pause, RotateCcw, TrendingUp, Target, Clock, DollarSign, Brain, Search } from 'lucide-react'

const InteractiveDemo: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false)
  const [currentIteration, setCurrentIteration] = useState(0)
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('dspy')
  const [metrics, setMetrics] = useState({
    latency: 0.85,
    cost: 0.65,
    accuracy: 0.92,
    score: 0.81,
    context_efficiency: 0.65,
    compression_ratio: 0.0
  })

  const algorithms = [
    { id: 'dspy', name: 'DSPy', color: 'blue', description: 'AI-powered optimization with artifacts' },
    { id: 'context-aware', name: 'Context Aware', color: 'indigo', description: 'Self-optimizing with context analysis' },
    { id: 'context-compression', name: 'Context Compression', color: 'emerald', description: 'Optimize context size and efficiency' },
    { id: 'hillclimb', name: 'Hill Climb', color: 'green', description: 'Gradient-based parameter tuning' },
    { id: 'bandit', name: 'Bandit', color: 'purple', description: 'Multi-armed bandit exploration' }
  ]

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRunning) {
      interval = setInterval(() => {
        setCurrentIteration(prev => prev + 1)
        // Simulate optimization progress
        setMetrics(prev => {
          const isContextAlgorithm = selectedAlgorithm.includes('context')
          return {
            latency: Math.max(0.1, prev.latency - Math.random() * 0.02),
            cost: Math.max(0.1, prev.cost - Math.random() * 0.015),
            accuracy: Math.min(0.99, prev.accuracy + Math.random() * 0.01),
            score: Math.min(0.99, prev.score + Math.random() * 0.005),
            context_efficiency: isContextAlgorithm 
              ? Math.min(0.99, prev.context_efficiency + Math.random() * 0.02)
              : prev.context_efficiency,
            compression_ratio: isContextAlgorithm && prev.compression_ratio === 0
              ? Math.random() * 0.7
              : prev.compression_ratio
          }
        })
      }, 500)
    }
    return () => clearInterval(interval)
  }, [isRunning])

  const resetDemo = () => {
    setIsRunning(false)
    setCurrentIteration(0)
    setMetrics({
      latency: 0.85,
      cost: 0.65,
      accuracy: 0.92,
      score: 0.81,
      context_efficiency: 0.65,
      compression_ratio: 0.0
    })
  }

  const currentAlgorithm = algorithms.find(a => a.id === selectedAlgorithm)

  return (
    <section className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Interactive Optimization Demo
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Experience the optimization process in real-time including context introspection. 
            Watch how different algorithms explore the parameter space and improve performance 
            across traditional and context-aware metrics.
          </p>
        </div>

        <div className="interactive-demo">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Controls */}
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-4">Algorithm Selection</h3>
                <div className="grid grid-cols-1 gap-3">
                  {algorithms.map((algorithm) => (
                    <button
                      key={algorithm.id}
                      onClick={() => setSelectedAlgorithm(algorithm.id)}
                      className={`p-4 rounded-lg border-2 text-left transition-all duration-200 ${
                        selectedAlgorithm === algorithm.id
                          ? `border-${algorithm.color}-500 bg-${algorithm.color}-50`
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <div className="font-semibold text-slate-900">{algorithm.name}</div>
                      <div className="text-sm text-slate-600 mt-1">{algorithm.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-4">Controls</h3>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setIsRunning(!isRunning)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                      isRunning
                        ? 'bg-red-500 hover:bg-red-600 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                  >
                    {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    <span>{isRunning ? 'Pause' : 'Start'}</span>
                  </button>
                  <button
                    onClick={resetDemo}
                    className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium transition-all duration-200"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Reset</span>
                  </button>
                </div>
              </div>

              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-sm text-slate-600 mb-2">Current Algorithm</div>
                <div className="font-semibold text-slate-900">{currentAlgorithm?.name}</div>
                <div className="text-sm text-slate-600 mt-2">Iteration: {currentIteration}</div>
              </div>
            </div>

            {/* Metrics Visualization */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-slate-900">Performance Metrics</h3>
              
              <div className="space-y-4">
                <MetricBar
                  label="Latency (P95)"
                  value={metrics.latency}
                  color="blue"
                  icon={Clock}
                  unit="s"
                  target={0.5}
                />
                <MetricBar
                  label="Cost per Request"
                  value={metrics.cost}
                  color="green"
                  icon={DollarSign}
                  unit="$"
                  target={0.3}
                />
                <MetricBar
                  label="Task Success Rate"
                  value={metrics.accuracy}
                  color="purple"
                  icon={Target}
                  unit="%"
                  target={0.95}
                />
                <MetricBar
                  label="Context Efficiency"
                  value={metrics.context_efficiency}
                  color="indigo"
                  icon={Brain}
                  unit="%"
                  target={0.9}
                />
                {metrics.compression_ratio > 0 && (
                  <MetricBar
                    label="Compression Ratio"
                    value={metrics.compression_ratio}
                    color="emerald"
                    icon={Search}
                    unit="%"
                    target={0.7}
                  />
                )}
                <MetricBar
                  label="Overall Score"
                  value={metrics.score}
                  color="orange"
                  icon={TrendingUp}
                  unit=""
                  target={0.9}
                />
              </div>

              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700">Optimization Progress</span>
                  <span className="text-sm text-slate-600">{Math.round(metrics.score * 100)}%</span>
                </div>
                <div className="mt-2 w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${metrics.score * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Algorithm Insights */}
        <div className="mt-12 bg-slate-50 rounded-2xl p-8">
          <h3 className="text-2xl font-semibold text-slate-900 mb-6">Algorithm Insights</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{currentIteration}</div>
              <div className="text-sm text-slate-600">Iterations Completed</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {((0.81 - metrics.score) / 0.81 * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-slate-600">Improvement</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {selectedAlgorithm === 'dspy' ? 'AI' : 
                 selectedAlgorithm === 'context-aware' ? 'Self-Aware' :
                 selectedAlgorithm === 'context-compression' ? 'Compression' :
                 selectedAlgorithm === 'hillclimb' ? 'Gradient' : 'Exploration'}
              </div>
              <div className="text-sm text-slate-600">Strategy</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

interface MetricBarProps {
  label: string
  value: number
  color: string
  icon: React.ElementType
  unit: string
  target: number
}

const MetricBar: React.FC<MetricBarProps> = ({ label, value, color, icon: Icon, unit, target }) => {
  const percentage = Math.min(100, (value / (target * 1.2)) * 100)
  const isImproving = value <= target

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className={`w-4 h-4 text-${color}-600`} />
          <span className="text-sm font-medium text-slate-700">{label}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm font-semibold text-slate-900">
            {unit === '%' ? `${Math.round(value * 100)}%` : value.toFixed(3) + unit}
          </span>
          <span className="text-xs text-slate-500">target: {target + unit}</span>
        </div>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            isImproving ? `bg-${color}-500` : 'bg-red-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

export default InteractiveDemo