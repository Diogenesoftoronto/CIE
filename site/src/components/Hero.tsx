import React from 'react'
import { ArrowDown, Play } from 'lucide-react'

const Hero: React.FC = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-600/20" />
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="mb-8">
          <span className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white/80 text-sm font-medium border border-white/20">
            <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
            Production Ready
          </span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          CIE: Optimization &
          <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Evaluation Framework
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-white/80 mb-12 max-w-3xl mx-auto leading-relaxed">
          An interactive framework for AI-powered optimization and evaluation with advanced context introspection.
          Transform AI agents into self-aware, self-optimizing systems with a premium Harlequin-inspired TUI and real-time prompt management.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
          <button className="group bg-white text-slate-900 px-8 py-4 rounded-lg font-semibold hover:bg-slate-100 transition-all duration-200 flex items-center space-x-2 hover:scale-105">
            <span>Get Started</span>
            <ArrowDown className="w-5 h-5 group-hover:translate-y-1 transition-transform" />
          </button>
          <button className="group bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-lg font-semibold hover:bg-white/20 transition-all duration-200 flex items-center space-x-2 border border-white/20 hover:scale-105">
            <Play className="w-5 h-5" />
            <span>View Demo</span>
          </button>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">101</div>
            <div className="text-white/70">Tests Passing</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">32%</div>
            <div className="text-white/70">Code Coverage</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">100%</div>
            <div className="text-white/70">Ruff Pass</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white mb-2">3+</div>
            <div className="text-white/70">Context Optimizers</div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white/50 rounded-full mt-2 animate-pulse" />
        </div>
      </div>
    </section>
  )
}

export default Hero