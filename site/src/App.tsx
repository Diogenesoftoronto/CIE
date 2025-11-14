import React from 'react'
import Header from './components/Header'
import Hero from './components/Hero'
import Introduction from './components/Introduction'
import Architecture from './components/Architecture'
import InteractiveDemo from './components/InteractiveDemo'
import Algorithms from './components/Algorithms'
import Evaluation from './components/Evaluation'
import Results from './components/Results'
import Conclusion from './components/Conclusion'
import Footer from './components/Footer'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200">
      <Header />
      <Hero />
      <Introduction />
      <Architecture />
      <InteractiveDemo />
      <Algorithms />
      <Evaluation />
      <Results />
      <Conclusion />
      <Footer />
    </div>
  )
}

export default App