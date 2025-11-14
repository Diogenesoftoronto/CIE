import React from 'react'
import { Github, BookOpen, Mail, Heart } from 'lucide-react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 text-slate-300 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">CIE</span>
              </div>
              <span className="font-semibold text-white">CIE Framework</span>
            </div>
            <p className="text-slate-400 leading-relaxed mb-4">
              An interactive framework for AI-powered optimization and evaluation of machine learning systems. 
              Built with modern Python and comprehensive CI/CD.
            </p>
            <div className="flex items-center space-x-2 text-sm text-slate-500">
              <span>Made with</span>
              <Heart className="w-4 h-4 text-red-500 fill-current" />
              <span>by the CIE team</span>
            </div>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold text-white mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <a href="#introduction" className="hover:text-white transition-colors duration-200">
                  Introduction
                </a>
              </li>
              <li>
                <a href="#architecture" className="hover:text-white transition-colors duration-200">
                  Architecture
                </a>
              </li>
              <li>
                <a href="#algorithms" className="hover:text-white transition-colors duration-200">
                  Algorithms
                </a>
              </li>
              <li>
                <a href="#evaluation" className="hover:text-white transition-colors duration-200">
                  Evaluation
                </a>
              </li>
            </ul>
          </div>

          {/* Community */}
          <div>
            <h3 className="font-semibold text-white mb-4">Community</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/your-repo/cie"
                  className="flex items-center space-x-2 hover:text-white transition-colors duration-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="w-4 h-4" />
                  <span>GitHub</span>
                </a>
              </li>
              <li>
                <a
                  href="https://cie.readthedocs.io"
                  className="flex items-center space-x-2 hover:text-white transition-colors duration-200"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <BookOpen className="w-4 h-4" />
                  <span>Documentation</span>
                </a>
              </li>
              <li>
                <a
                  href="mailto:team@cie.dev"
                  className="flex items-center space-x-2 hover:text-white transition-colors duration-200"
                >
                  <Mail className="w-4 h-4" />
                  <span>Contact</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-slate-400 text-sm">
            © 2024 CIE Framework. Open source under MIT License.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a
              href="https://github.com/your-repo/cie/blob/main/LICENSE"
              className="text-slate-400 hover:text-white text-sm transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              License
            </a>
            <a
              href="https://github.com/your-repo/cie/blob/main/CONTRIBUTING.md"
              className="text-slate-400 hover:text-white text-sm transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              Contributing
            </a>
            <a
              href="https://github.com/your-repo/cie/security"
              className="text-slate-400 hover:text-white text-sm transition-colors duration-200"
              target="_blank"
              rel="noopener noreferrer"
            >
              Security
            </a>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer