import React, { useState } from 'react'
import { BarChart3, TrendingUp, Target, Clock, DollarSign, XCircle, Activity, Brain, Search, FileText } from 'lucide-react'

const Evaluation: React.FC = () => {
  const [selectedWorkload, setSelectedWorkload] = useState('classification')
  const [evaluationResults] = useState({
    latency: { current: 0.45, baseline: 0.62, improvement: 27.4 },
    cost: { current: 0.023, baseline: 0.031, improvement: 25.8 },
    accuracy: { current: 0.94, baseline: 0.89, improvement: 5.6 },
    error_rate: { current: 0.02, baseline: 0.08, improvement: 75.0 },
    context_efficiency: { current: 0.87, baseline: 0.65, improvement: 33.8 },
    compression_ratio: { current: 0.68, baseline: 0.0, improvement: 68.0 },
    text_similarity: { current: 0.92, baseline: 0.85, improvement: 8.2 }
  })

  const workloads = [
    {
      id: 'classification',
      name: 'Text Classification',
      description: 'Multi-class text classification with varying complexity',
      items: 1000,
      metrics: ['accuracy', 'precision', 'recall', 'f1_score', 'text_similarity']
    },
    {
      id: 'generation',
      name: 'Text Generation',
      description: 'Long-form text generation with quality evaluation',
      items: 500,
      metrics: ['bleu_score', 'rouge_score', 'perplexity', 'coherence', 'text_similarity']
    },
    {
      id: 'reasoning',
      name: 'Reasoning Tasks',
      description: 'Multi-step reasoning and problem solving',
      items: 200,
      metrics: ['accuracy', 'step_coverage', 'logical_consistency']
    },
    {
      id: 'context-analysis',
      name: 'Context Analysis',
      description: 'Context introspection and optimization evaluation',
      items: 150,
      metrics: ['context_efficiency', 'compression_ratio', 'access_pattern_efficiency']
    }
  ]

  const metrics = [
    {
      key: 'latency',
      name: 'Latency (P95)',
      icon: Clock,
      color: 'blue',
      unit: 's',
      lower_is_better: true,
      description: '95th percentile response time'
    },
    {
      key: 'cost',
      name: 'Cost per Request',
      icon: DollarSign,
      color: 'green',
      unit: '$',
      lower_is_better: true,
      description: 'Average cost per API call'
    },
    {
      key: 'accuracy',
      name: 'Task Success Rate',
      icon: Target,
      color: 'purple',
      unit: '%',
      lower_is_better: false,
      description: 'Percentage of successful task completions'
    },
    {
      key: 'error_rate',
      name: 'Error Rate',
      icon: XCircle,
      color: 'red',
      unit: '%',
      lower_is_better: true,
      description: 'Percentage of failed operations'
    },
    {
      key: 'context_efficiency',
      name: 'Context Efficiency',
      icon: Brain,
      color: 'indigo',
      unit: '%',
      lower_is_better: false,
      description: 'Context organization and access efficiency'
    },
    {
      key: 'compression_ratio',
      name: 'Compression Ratio',
      icon: Search,
      color: 'emerald',
      unit: '%',
      lower_is_better: false,
      description: 'Context size reduction while preserving information'
    },
    {
      key: 'text_similarity',
      name: 'Text Similarity',
      icon: FileText,
      color: 'orange',
      unit: '%',
      lower_is_better: false,
      description: 'Similarity between generated and reference text'
    }
  ]

  const currentWorkload = workloads.find(w => w.id === selectedWorkload)

  return (
    <section id="evaluation" className="py-20 bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Comprehensive Evaluation
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Multi-dimensional evaluation including advanced context introspection metrics. 
            Compare optimized policies against baselines with detailed performance analysis 
            across traditional and context-aware dimensions.
          </p>
        </div>

        {/* Workload Selection */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold text-slate-900 mb-6">Evaluation Workloads</h3>
          <div className="grid md:grid-cols-3 gap-6">
            {workloads.map((workload) => (
              <div
                key={workload.id}
                className={`distill-card rounded-xl p-6 cursor-pointer transition-all duration-200 ${
                  selectedWorkload === workload.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
                onClick={() => setSelectedWorkload(workload.id)}
              >
                <h4 className="text-lg font-semibold text-slate-900 mb-2">{workload.name}</h4>
                <p className="text-slate-600 text-sm mb-4">{workload.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-500">{workload.items} items</span>
                  <div className="flex space-x-1">
                    {workload.metrics.slice(0, 3).map((metric, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded"
                      >
                        {metric}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics Dashboard */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-slate-900">Performance Metrics</h3>
            {metrics.map((metric) => {
              const result = evaluationResults[metric.key as keyof typeof evaluationResults]
              const Icon = metric.icon
              const improvement = result.improvement
              const isPositive = metric.lower_is_better ? improvement > 0 : improvement > 0

              return (
                <div key={metric.key} className="distill-card rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-10 h-10 bg-${metric.color}-100 rounded-lg flex items-center justify-center`}>
                        <Icon className={`w-5 h-5 text-${metric.color}-600`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-900">{metric.name}</h4>
                        <p className="text-sm text-slate-600">{metric.description}</p>
                      </div>
                    </div>
                    <div className={`flex items-center space-x-1 text-sm font-medium ${
                      isPositive ? 'text-green-600' : 'text-red-600'
                    }`}>
                      <TrendingUp className="w-4 h-4" />
                      <span>{improvement > 0 ? '+' : ''}{improvement.toFixed(1)}%</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Current</span>
                      <span className="font-semibold text-slate-900">
                        {result.current.toFixed(3)}{metric.unit}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-600">Baseline</span>
                      <span className="text-slate-600">
                        {result.baseline.toFixed(3)}{metric.unit}
                      </span>
                    </div>
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full bg-${metric.color}-500`}
                        style={{
                          width: `${Math.min(100, (result.current / (result.baseline * 1.2)) * 100)}%`
                        }}
                      />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-slate-900">Evaluation Process</h3>
            
            <div className="space-y-4">
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-600 font-semibold text-sm">1</span>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Workload Selection</h4>
                  <p className="text-sm text-slate-600">Choose evaluation workload based on your use case</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 font-semibold text-sm">2</span>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Policy Application</h4>
                  <p className="text-sm text-slate-600">Apply optimized policy to the selected workload</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-purple-600 font-semibold text-sm">3</span>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Metric Collection</h4>
                  <p className="text-sm text-slate-600">Gather performance metrics across all dimensions</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-orange-600 font-semibold text-sm">4</span>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Comparative Analysis</h4>
                  <p className="text-sm text-slate-600">Compare against baseline and previous iterations</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
              <h4 className="text-lg font-semibold text-slate-900 mb-4">Current Workload</h4>
              {currentWorkload && (
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-slate-600">Name:</span>
                    <span className="ml-2 font-medium text-slate-900">{currentWorkload.name}</span>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Items:</span>
                    <span className="ml-2 font-medium text-slate-900">{currentWorkload.items}</span>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Metrics:</span>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {currentWorkload.metrics.map((metric, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-white text-slate-700 text-xs rounded border"
                        >
                          {metric}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Evaluation Results Summary */}
        <div className="bg-white rounded-2xl p-8 shadow-lg">
          <h3 className="text-2xl font-semibold text-slate-900 mb-6">Overall Results</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">94.2%</div>
              <div className="text-sm text-slate-600">Overall Score</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">33.2%</div>
              <div className="text-sm text-slate-600">Avg Improvement</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">4/4</div>
              <div className="text-sm text-slate-600">Metrics Improved</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">1,000</div>
              <div className="text-sm text-slate-600">Evaluations</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Evaluation