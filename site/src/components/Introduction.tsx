import React from 'react'
import { ArrowRight, Zap, Target, BarChart3, Brain } from 'lucide-react'

const Introduction: React.FC = () => {
  return (
    <section id="introduction" className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            The Challenge of ML Optimization
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Modern machine learning systems require careful optimization across multiple objectives: 
            latency, cost, accuracy, and resource usage. Traditional approaches often optimize for 
            single metrics, missing the complex trade-offs that define real-world performance.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          <div className="distill-card rounded-xl p-8 distill-hover">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-4">Multi-Objective Optimization</h3>
            <p className="text-slate-600 leading-relaxed">
              Balance competing objectives like latency, cost, and accuracy through 
              weighted scoring functions and Pareto frontier analysis.
            </p>
          </div>

          <div className="distill-card rounded-xl p-8 distill-hover">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-4">AI-Powered Algorithms</h3>
            <p className="text-slate-600 leading-relaxed">
              Leverage state-of-the-art optimization algorithms including DSPy, Hill Climbing, 
              and Multi-Armed Bandits with real AI model integration.
            </p>
          </div>

          <div className="distill-card rounded-xl p-8 distill-hover">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-4">Interactive Evaluation</h3>
            <p className="text-slate-600 leading-relaxed">
              Real-time evaluation with comprehensive metrics, interactive visualizations, 
              and detailed performance analysis across different workloads.
            </p>
          </div>

          <div className="distill-card rounded-xl p-8 distill-hover">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
              <Brain className="w-6 h-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-900 mb-4">Context Introspection</h3>
            <p className="text-slate-600 leading-relaxed">
              Advanced context analysis and manipulation tools that enable agents to understand 
              and optimize their own operational context in real-time.
            </p>
          </div>
        </div>

        {/* Problem Statement */}
        <div className="bg-slate-50 rounded-2xl p-8 md:p-12">
          <h3 className="text-2xl font-semibold text-slate-900 mb-6">The Context Introspection Challenge</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="text-lg font-medium text-slate-800 mb-4">Traditional Agent Limitations</h4>
              <ul className="space-y-3 text-slate-600">
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Agents operate as passive responders without self-awareness</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>No visibility into context usage, tools, or system resources</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Manual optimization without introspective capabilities</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                  <span>Limited ability to adapt and optimize their own behavior</span>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-medium text-slate-800 mb-4">CIE's Introspective Solution</h4>
              <ul className="space-y-3 text-slate-600">
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Real-time context analysis and window usage monitoring</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Self-optimizing agents with metacognitive capabilities</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Automated context compression and organization</span>
                </li>
                <li className="flex items-start space-x-3">
                  <ArrowRight className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>Interactive dashboard for human-agent collaboration</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Introduction