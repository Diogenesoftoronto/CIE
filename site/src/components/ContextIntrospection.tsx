import React, { useState } from 'react'
import { Brain, Search, Zap, Eye, GitBranch, Layers, Activity, Target } from 'lucide-react'

const ContextIntrospection: React.FC = () => {
  const [selectedTool, setSelectedTool] = useState('inspect')

  const contextTools = [
    {
      id: 'inspect',
      name: 'Context Inspector',
      icon: Eye,
      color: 'blue',
      description: 'Analyze context structure and identify optimization opportunities',
      features: [
        'Hierarchical context tree visualization',
        'Access pattern analysis and hotspot detection',
        'Context efficiency scoring (0-1 scale)',
        'Real-time size and complexity monitoring'
      ],
      code: `def inspect_context(path: str, max_depth: int = 5) -> Dict:
    """Analyze context structure and efficiency"""
    analysis = introspector.analyze(path, max_depth)
    
    return {
        'summary': {
            'total_nodes': analysis.node_count,
            'total_size': analysis.size_bytes,
            'efficiency_score': analysis.efficiency
        },
        'hotspots': analysis.get_hotspots(5),
        'optimization_potential': analysis.potential,
        'access_patterns': analysis.patterns
    }`
    },
    {
      id: 'compress',
      name: 'Context Compression',
      icon: Search,
      color: 'green',
      description: 'Reduce context size while preserving essential information',
      features: [
        'Multi-strategy compression (frequency, type, hierarchical)',
        'Adaptive threshold adjustment',
        'Information preservation validation',
        'Compression ratio optimization'
      ],
      code: `def compress_context(strategy: str, threshold: int = 1000) -> Dict:
    """Apply context compression strategies"""
    strategies = ['frequency-based', 'type-based', 'hierarchical']
    
    best_compression = None
    best_ratio = 0.0
    
    for strategy in strategies:
        compression = manipulator.compress(
            strategy=strategy,
            threshold=threshold
        )
        if compression['ratio'] > best_ratio:
            best_ratio = compression['ratio']
            best_compression = compression
    
    return {
        'strategy': best_compression['strategy'],
        'compression_ratio': best_ratio,
        'preserved_paths': best_compression['preserved']
    }`
    },
    {
      id: 'optimize',
      name: 'Context Optimizer',
      icon: Zap,
      color: 'purple',
      description: 'Automatically optimize context organization and access patterns',
      features: [
        'Frequency-based organization and caching',
        'Semantic clustering and relationship mapping',
        'Access pattern learning and prediction',
        'Multi-level caching with LRU eviction'
      ],
      code: `def optimize_context() -> Dict:
    """Run full context optimization pipeline"""
    # Analyze current state
    analysis = inspect_context('/')
    
    # Apply optimizations based on analysis
    actions = []
    
    if analysis['optimization_potential'] > 0.5:
        # Compress large contexts
        compression = compress_context('auto')
        actions.append({
            'type': 'compression',
            'compression_ratio': compression['ratio']
        })
    
    # Reorganize by access patterns
    reorganization = reorganize_by_frequency()
    actions.append({
        'type': 'reorganization',
        'efficiency_gain': reorganization['efficiency_gain']
    })
    
    return {
        'actions': actions,
        'final_efficiency': calculate_efficiency(),
        'performance_improvement': measure_improvement()
    }`
    },
    {
      id: 'navigate',
      name: 'Context Navigator',
      icon: GitBranch,
      color: 'orange',
      description: 'Navigate context like a filesystem with advanced search capabilities',
      features: [
        'Filesystem-like navigation (ls, cd, pwd, find)',
        'Advanced path querying and filtering',
        'Context diffing and versioning support',
        'Interactive context exploration'
      ],
      code: `def navigate_context(command: str) -> str:
    """Navigate context like a filesystem"""
    parts = command.split()
    operation = parts[0]
    
    if operation == 'ls':
        path = parts[1] if len(parts) > 1 else '/'
        return list_directory(path)
    elif operation == 'cd':
        path = parts[1] if len(parts) > 1 else '/'
        return change_directory(path)
    elif operation == 'find':
        pattern = parts[1] if len(parts) > 1 else '*'
        return find_items(pattern)
    elif operation == 'pwd':
        return get_current_path()
    
    return f"Unknown command: {operation}"`
    }
  ]

  const currentTool = contextTools.find(tool => tool.id === selectedTool)

  return (
    <section id="context-introspection" className="py-20 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
              <Brain className="w-8 h-8 text-indigo-600" />
            </div>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Context Introspection & Manipulation
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Advanced tools for analyzing, optimizing, and navigating agent context. Transform AI agents 
            from passive responders into self-aware, self-optimizing computational systems.
          </p>
        </div>

        {/* Tool Selector */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex bg-slate-100 rounded-lg p-1">
            {contextTools.map((tool) => {
              const Icon = tool.icon
              return (
                <button
                  key={tool.id}
                  onClick={() => setSelectedTool(tool.id)}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-md transition-all duration-200 ${
                    selectedTool === tool.id
                      ? `bg-white shadow-sm text-${tool.color}-600`
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tool.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Tool Details */}
        {currentTool && (
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Left Column - Overview */}
            <div className="space-y-8">
              <div className="distill-card rounded-xl p-8">
                <div className="flex items-center mb-6">
                  <div className={`w-12 h-12 bg-${currentTool.color}-100 rounded-lg flex items-center justify-center mr-4`}>
                    <currentTool.icon className={`w-6 h-6 text-${currentTool.color}-600`} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-slate-900">{currentTool.name}</h3>
                    <p className="text-slate-600">{currentTool.description}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="text-lg font-medium text-slate-800">Key Features</h4>
                  <div className="grid grid-cols-1 gap-3">
                    {currentTool.features.map((feature, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className={`w-2 h-2 bg-${currentTool.color}-500 rounded-full mt-2 flex-shrink-0`} />
                        <span className="text-slate-600">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6">
                <h4 className="text-lg font-semibold text-slate-900 mb-4">Use Cases</h4>
                <div className="space-y-3 text-slate-600">
                  {selectedTool === 'inspect' && (
                    <>
                      <p>• Monitor context window usage in real-time</p>
                      <p>• Identify memory leaks and inefficient patterns</p>
                      <p>• Analyze agent decision-making context</p>
                      <p>• Optimize context organization for faster access</p>
                    </>
                  )}
                  {selectedTool === 'compress' && (
                    <>
                      <p>• Reduce context size for faster processing</p>
                      <p>• Preserve essential information during compression</p>
                      <p>• Optimize memory usage in resource-constrained environments</p>
                      <p>• Maintain context quality while reducing size</p>
                    </>
                  )}
                  {selectedTool === 'optimize' && (
                    <>
                      <p>• Automatically improve context organization</p>
                      <p>• Learn from access patterns to optimize layout</p>
                      <p>• Implement adaptive caching strategies</p>
                      <p>• Enhance overall system performance</p>
                    </>
                  )}
                  {selectedTool === 'navigate' && (
                    <>
                      <p>• Explore complex context structures interactively</p>
                      <p>• Search for specific information within context</p>
                      <p>• Navigate hierarchical data efficiently</p>
                      <p>• Debug and inspect agent state</p>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - Code Example */}
            <div>
              <div className="distill-card rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-medium text-slate-800">Implementation</h4>
                  <div className="flex items-center space-x-2">
                    <Activity className="w-5 h-5 text-slate-400" />
                    <span className="text-sm text-slate-500">Python</span>
                  </div>
                </div>
                <div className="code-block">
                  <pre className="text-sm">{currentTool.code}</pre>
                </div>
              </div>

              <div className="mt-6 distill-card rounded-xl p-6">
                <h4 className="text-lg font-medium text-slate-800 mb-4">Integration Example</h4>
                <div className="code-block">
                  <pre>{`# Initialize context tools
tools = AgentContextTools()

# Inspect current context
analysis = tools.inspect_context('current', max_depth=5)
print(f"Context efficiency: {analysis['summary']['efficiency_score']:.2f}")

# Optimize if needed
if analysis['optimization_potential'] > 0.5:
    optimization = tools.optimize_context()
    print(f"Applied {len(optimization['actions'])} optimization actions")
    print(f"Performance improvement: {optimization['performance_improvement']:.1f}%")

# Navigate context
result = tools.navigate_context('find policy')
print(f"Found {len(result)} policy-related items")`}</pre>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Context Metrics Dashboard */}
        <div className="mt-16 bg-gradient-to-r from-slate-50 to-indigo-50 rounded-2xl p-8">
          <h3 className="text-2xl font-semibold text-slate-900 mb-6 text-center">Context Introspection Metrics</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Layers className="w-8 h-8 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">0.87</div>
              <div className="text-sm text-slate-600">Context Efficiency</div>
              <div className="text-xs text-blue-600 font-medium">+33% vs baseline</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">68%</div>
              <div className="text-sm text-slate-600">Compression Ratio</div>
              <div className="text-xs text-green-600 font-medium">Size reduction</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-purple-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">94%</div>
              <div className="text-sm text-slate-600">Access Efficiency</div>
              <div className="text-xs text-purple-600 font-medium">Pattern optimized</div>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-slate-900 mb-2">2.3x</div>
              <div className="text-sm text-slate-600">Speed Improvement</div>
              <div className="text-xs text-orange-600 font-medium">Navigation optimized</div>
            </div>
          </div>
          <div className="mt-6 text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white rounded-lg border border-indigo-200">
              <div className="w-2 h-2 bg-indigo-500 rounded-full mr-2"></div>
              <span className="text-sm font-medium text-indigo-700">Context introspection enables self-optimizing agents</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default ContextIntrospection