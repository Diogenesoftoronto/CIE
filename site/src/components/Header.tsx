import React, { useState, useEffect } from 'react'
import { Menu, X, Github, BookOpen } from 'lucide-react'

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { name: 'Introduction', href: '#introduction' },
    { name: 'Architecture', href: '#architecture' },
    { name: 'Algorithms', href: '#algorithms' },
    { name: 'Evaluation', href: '#evaluation' },
    { name: 'Results', href: '#results' },
  ]

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled ? 'bg-white/90 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CIE</span>
            </div>
            <span className="font-semibold text-slate-800">CIE Framework</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium"
              >
                {item.name}
              </a>
            ))}
          </nav>

          <div className="hidden md:flex items-center space-x-4">
            <a
              href="https://github.com/your-repo/cie"
              className="text-slate-600 hover:text-slate-900 transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="https://cie.readthedocs.io"
              className="text-slate-600 hover:text-slate-900 transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              <BookOpen className="w-5 h-5" />
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden bg-white/95 backdrop-blur-md rounded-lg mt-2 p-4 shadow-lg">
            <nav className="flex flex-col space-y-4">
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </a>
              ))}
              <div className="flex space-x-4 pt-4 border-t border-slate-200">
                <a
                  href="https://github.com/your-repo/cie"
                  className="text-slate-600 hover:text-slate-900 transition-colors duration-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="w-5 h-5" />
                </a>
                <a
                  href="https://cie.readthedocs.io"
                  className="text-slate-600 hover:text-slate-900 transition-colors duration-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <BookOpen className="w-5 h-5" />
                </a>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}

export default Header