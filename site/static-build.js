#!/usr/bin/env node

// Simple static build script for the CIE documentation site
// This creates a static version that can be deployed anywhere

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🚀 Building CIE Documentation Site...');

// Create dist directory
const distDir = path.join(__dirname, 'dist');
if (fs.existsSync(distDir)) {
  fs.rmSync(distDir, { recursive: true });
}
fs.mkdirSync(distDir, { recursive: true });

// Copy index.html
const indexHtml = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
fs.writeFileSync(path.join(distDir, 'index.html'), indexHtml);

// Create a simple CSS file with all the styles
const cssContent = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --distill-blue: #3b82f6;
  --distill-orange: #f59e0b;
  --distill-green: #10b981;
  --distill-purple: #8b5cf6;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  line-height: 1.6;
  color: #334155;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Header */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  background: white/90;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 4rem;
  padding: 0 1rem;
}

.nav-brand {
  display: flex;
  align-items: center;
  space-gap: 0.5rem;
}

.nav-logo {
  width: 2rem;
  height: 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 0.875rem;
}

/* Hero Section */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #7c3aed 100%);
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  color: white;
  max-width: 4xl;
  padding: 0 1rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

@media (min-width: 768px) {
  .hero-title {
    font-size: 4.5rem;
  }
}

.gradient-text {
  background: linear-gradient(135deg, #60a5fa 0%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  color: #cbd5e1;
  margin-bottom: 3rem;
  max-width: 42rem;
  margin-left: auto;
  margin-right: auto;
}

.hero-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 4rem;
}

@media (min-width: 640px) {
  .hero-buttons {
    flex-direction: row;
    justify-content: center;
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-primary {
  background: white;
  color: #0f172a;
}

.btn-primary:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* Metrics */
.metrics {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 2rem;
  text-align: center;
}

@media (min-width: 768px) {
  .metrics {
    grid-template-columns: repeat(3, 1fr);
  }
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.metric-label {
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Sections */
.section {
  padding: 5rem 0;
}

.section-title {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1.5rem;
  color: #0f172a;
}

@media (min-width: 768px) {
  .section-title {
    font-size: 3rem;
  }
}

.section-description {
  font-size: 1.25rem;
  text-align: center;
  color: #64748b;
  max-width: 42rem;
  margin: 0 auto 4rem;
}

/* Cards */
.card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* Code blocks */
.code-block {
  background: #0f172a;
  color: #f8fafc;
  border-radius: 0.5rem;
  padding: 1.5rem;
  overflow-x: auto;
  font-family: 'JetBrains Mono', Monaco, Consolas, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 1.5rem 0;
}

/* Interactive demo */
.demo {
  border: 2px solid #3b82f6;
  border-radius: 1rem;
  padding: 2rem;
  background: rgba(59, 130, 246, 0.05);
  margin: 2rem 0;
}

/* Footer */
.footer {
  background: #020617;
  color: #cbd5e1;
  padding: 3rem 0;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 2rem;
}

@media (min-width: 768px) {
  .footer-content {
    grid-template-columns: repeat(4, 1fr);
  }
}

.footer-title {
  color: white;
  font-weight: 600;
  margin-bottom: 1rem;
}

.footer-link {
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: white;
}

.footer-bottom {
  border-top: 1px solid #1e293b;
  margin-top: 2rem;
  padding-top: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

/* Utilities */
.text-center { text-align: center; }
.text-white { color: white; }
.text-slate-900 { color: #0f172a; }
.text-slate-600 { color: #475569; }
.text-slate-400 { color: #94a3b8; }

.bg-white { background: white; }
.bg-slate-50 { background: #f8fafc; }
.bg-slate-900 { background: #0f172a; }

.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }

.rounded-lg { border-radius: 0.5rem; }
.rounded-xl { border-radius: 1rem; }

.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }

.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
.gap-8 { gap: 2rem; }

.flex { display: flex; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.space-x-2 > * + * { margin-left: 0.5rem; }
.space-y-2 > * + * { margin-top: 0.5rem; }
.space-y-4 > * + * { margin-top: 1rem; }

@media (min-width: 640px) {
  .sm\\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 768px) {
  .md\\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
  .md\\:grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
  .md\\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% { transform: translateY(0); }
  40%, 43% { transform: translateY(-8px); }
  70% { transform: translateY(-4px); }
}

.animate-fadeIn { animation: fadeIn 0.6s ease-out; }
.animate-pulse { animation: pulse 2s infinite; }
.animate-bounce { animation: bounce 2s infinite; }
`;

// Write CSS file
fs.writeFileSync(path.join(distDir, 'styles.css'), cssContent);

// Create a simple JavaScript file for interactivity
const jsContent = `
// Simple interactivity for CIE Documentation Site

document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 CIE Documentation Site loaded!');
  
  // Add smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Add scroll spy for navigation
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('nav a[href^="#"]');
  
  function updateActiveNav() {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (window.scrollY >= sectionTop - 200) {
        current = section.getAttribute('id');
      }
    });
    
    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + current) {
        link.classList.add('active');
      }
    });
  }
  
  window.addEventListener('scroll', updateActiveNav);
  updateActiveNav(); // Initial call
});
`;

fs.writeFileSync(path.join(distDir, 'script.js'), jsContent);

// Create a simple HTML file with all the content embedded
const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CIE: Optimization & Evaluation Framework</title>
    <meta name="description" content="An interactive framework for AI-powered optimization and evaluation of machine learning systems">
    <link rel="stylesheet" href="styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <nav class="nav container">
            <div class="nav-brand">
                <div class="nav-logo">CIE</div>
                <span class="font-semibold text-slate-900">CIE Framework</span>
            </div>
            <div class="hidden md:flex items-center space-x-8">
                <a href="#introduction" class="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium">Introduction</a>
                <a href="#architecture" class="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium">Architecture</a>
                <a href="#algorithms" class="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium">Algorithms</a>
                <a href="#evaluation" class="text-slate-600 hover:text-slate-900 transition-colors duration-200 font-medium">Evaluation</a>
            </div>
        </nav>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-bg"></div>
        <div class="hero-content animate-fadeIn">
            <div class="mb-8">
                <span class="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-white/80 text-sm font-medium border border-white/20">
                    <span class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                    Production Ready
                </span>
            </div>
            
            <h1 class="hero-title">
                CIE: Optimization &
                <span class="gradient-text">Evaluation Framework</span>
            </h1>
            
            <p class="hero-description">
                An interactive framework for AI-powered optimization and evaluation of machine learning systems. 
                Built with modern Python, featuring real AI model integration and comprehensive CI/CD.
            </p>
            
            <div class="hero-buttons">
                <a href="#introduction" class="btn btn-primary">Get Started</a>
                <a href="#interactive-demo" class="btn btn-secondary">View Demo</a>
            </div>
            
            <div class="metrics">
                <div>
                    <div class="metric-value">3+</div>
                    <div class="metric-label">AI Models</div>
                </div>
                <div>
                    <div class="metric-value">25%</div>
                    <div class="metric-label">Test Coverage</div>
                </div>
                <div>
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Ruff Pass</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Introduction Section -->
    <section id="introduction" class="section bg-white">
        <div class="container">
            <h2 class="section-title">The Challenge of ML Optimization</h2>
            <p class="section-description">
                Modern machine learning systems require careful optimization across multiple objectives: 
                latency, cost, accuracy, and resource usage. Traditional approaches often optimize for 
                single metrics, missing the complex trade-offs that define real-world performance.
            </p>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="card">
                    <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-slate-900 mb-4">Multi-Objective Optimization</h3>
                    <p class="text-slate-600 leading-relaxed">
                        Balance competing objectives like latency, cost, and accuracy through 
                        weighted scoring functions and Pareto frontier analysis.
                    </p>
                </div>
                
                <div class="card">
                    <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-slate-900 mb-4">AI-Powered Algorithms</h3>
                    <p class="text-slate-600 leading-relaxed">
                        Leverage state-of-the-art optimization algorithms including DSPy, Hill Climbing, 
                        and Multi-Armed Bandits with real AI model integration.
                    </p>
                </div>
                
                <div class="card">
                    <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-slate-900 mb-4">Interactive Evaluation</h3>
                    <p class="text-slate-600 leading-relaxed">
                        Real-time evaluation with comprehensive metrics, interactive visualizations, 
                        and detailed performance analysis across different workloads.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Architecture Section -->
    <section id="architecture" class="section bg-slate-50">
        <div class="container">
            <h2 class="section-title">System Architecture</h2>
            <p class="section-description">
                A modular, protocol-based architecture that separates concerns while maintaining 
                flexibility and extensibility. Built with modern Python practices and comprehensive 
                type safety.
            </p>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="card">
                    <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-900 mb-2">User Interface</h3>
                    <p class="text-sm text-slate-600">Interactive TUI and web interface for experiment management</p>
                </div>
                
                <div class="card">
                    <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-900 mb-2">Backend Core</h3>
                    <p class="text-sm text-slate-600">Central orchestration and state management</p>
                </div>
                
                <div class="card">
                    <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-900 mb-2">Optimization Layer</h3>
                    <p class="text-sm text-slate-600">AI-powered optimization algorithms</p>
                </div>
                
                <div class="card">
                    <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                        <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-900 mb-2">Data Layer</h3>
                    <p class="text-sm text-slate-600">Flexible storage and persistence</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="md:col-span-2">
                    <div class="flex items-center space-x-2 mb-4">
                        <div class="nav-logo">CIE</div>
                        <span class="font-semibold text-white">CIE Framework</span>
                    </div>
                    <p class="text-slate-400 leading-relaxed mb-4">
                        An interactive framework for AI-powered optimization and evaluation of machine learning systems. 
                        Built with modern Python and comprehensive CI/CD.
                    </p>
                    <div class="flex items-center space-x-2 text-sm text-slate-500">
                        <span>Made with</span>
                        <svg class="w-4 h-4 text-red-500 fill-current" viewBox="0 0 24 24">
                            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                        </svg>
                        <span>by the CIE team</span>
                    </div>
                </div>
                
                <div>
                    <h3 class="footer-title">Resources</h3>
                    <ul class="space-y-2">
                        <li><a href="#introduction" class="footer-link">Introduction</a></li>
                        <li><a href="#architecture" class="footer-link">Architecture</a></li>
                        <li><a href="#algorithms" class="footer-link">Algorithms</a></li>
                        <li><a href="#evaluation" class="footer-link">Evaluation</a></li>
                    </ul>
                </div>
                
                <div>
                    <h3 class="footer-title">Community</h3>
                    <ul class="space-y-2">
                        <li><a href="https://github.com/your-repo/cie" class="footer-link" target="_blank" rel="noopener noreferrer">GitHub</a></li>
                        <li><a href="https://cie.readthedocs.io" class="footer-link" target="_blank" rel="noopener noreferrer">Documentation</a></li>
                        <li><a href="mailto:team@cie.dev" class="footer-link">Contact</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p>© 2024 CIE Framework. Open source under MIT License.</p>
            </div>
        </div>
    </footer>

    <script src="script.js"></script>
</body>
</html>`;

fs.writeFileSync(path.join(distDir, 'index.html'), htmlContent);

console.log('✅ Static site built successfully!');
console.log('📁 Output directory: dist/');
console.log('🌐 Open dist/index.html in your browser to view the site');
console.log('');
console.log('Features included:');
console.log('• Responsive design with mobile support');
console.log('• Smooth scrolling navigation');
console.log('• Interactive elements and animations');
console.log('• Modern gradient aesthetics');
console.log('• Optimized for performance');
console.log('');
console.log('To deploy: Upload the entire dist/ folder to your web server or hosting platform.');