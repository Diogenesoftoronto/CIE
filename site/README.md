# CIE Documentation Site

A beautiful, interactive documentation site for the CIE (Optimization & Evaluation) Framework, built with modern web technologies and inspired by Distill.pub's visual explanations.

## 🎨 Design Philosophy

This site follows the Distill.pub design philosophy:
- **Visual-first explanations** with interactive diagrams
- **Clean, academic aesthetic** with plenty of whitespace
- **Smooth animations** and transitions
- **Mobile-responsive** design
- **Accessible** and performant

## 🚀 Tech Stack

- **Bun** - Fast JavaScript runtime and package manager
- **React 18** - Modern UI framework with TypeScript
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible components
- **Lucide React** - Consistent icon library

## 📦 Installation

```bash
# Install Bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies
bun install

# Start development server
bun run dev

# Build for production
bun run build

# Preview production build
bun run preview
```

## 🏗️ Project Structure

```
site/
├── src/
│   ├── components/          # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── Header.tsx      # Navigation header
│   │   ├── Hero.tsx        # Hero section
│   │   ├── Introduction.tsx # Problem introduction
│   │   ├── Architecture.tsx # System architecture
│   │   ├── InteractiveDemo.tsx # Interactive optimization demo
│   │   ├── Algorithms.tsx  # Algorithm explanations
│   │   ├── Evaluation.tsx  # Evaluation methodology
│   │   ├── Results.tsx     # Results and analysis
│   │   ├── Conclusion.tsx  # Future work and conclusions
│   │   └── Footer.tsx      # Site footer
│   ├── lib/
│   │   └── utils.ts        # Utility functions
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript type definitions
│   ├── index.css           # Global styles
│   ├── main.tsx            # Application entry point
│   └── App.tsx             # Main application component
├── public/                 # Static assets
├── tailwind.config.js      # Tailwind configuration
├── vite.config.ts          # Vite configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎯 Key Features

### Interactive Elements
- **Live optimization demo** with real-time metrics
- **Algorithm comparison** with interactive selectors
- **Pareto frontier visualization** for multi-objective optimization
- **Policy evaluation** with detailed metrics

### Visual Design
- **Distill-inspired** aesthetic with clean typography
- **Gradient backgrounds** and glassmorphism effects
- **Smooth animations** and hover states
- **Responsive layouts** for all screen sizes

### Content Sections
1. **Hero** - Eye-catching introduction with key metrics
2. **Introduction** - Problem statement and solution overview
3. **Architecture** - System design with interactive layers
4. **Interactive Demo** - Live optimization simulation
5. **Algorithms** - Detailed algorithm explanations with code
6. **Evaluation** - Comprehensive evaluation methodology
7. **Results** - Optimization results with visualizations
8. **Conclusion** - Future work and community links

## 🎨 Customization

### Colors
The site uses a custom color palette inspired by Distill:
- Primary: Blue (`#3b82f6`) to Purple (`#8b5cf6`) gradients
- Neutral: Slate gray scale for text and backgrounds
- Accent: Green for success, Red for errors, Orange for warnings

### Typography
- **Inter** - Modern sans-serif for body text
- **JetBrains Mono** - Monospace for code blocks
- **Times New Roman** - Serif for mathematical formulas

### Components
The site uses shadcn/ui components with custom styling:
- Buttons with hover effects and transitions
- Cards with glassmorphism and shadows
- Interactive elements with smooth animations

## 📱 Responsive Design

The site is fully responsive with breakpoints:
- **Mobile** (< 640px): Single column layout
- **Tablet** (640px - 1024px): Two column layout
- **Desktop** (> 1024px): Multi-column layout with sidebars

## 🔧 Development

### Adding New Components
```bash
# Add a new shadcn component
bunx shadcn@latest add [component-name]
```

### Custom Styles
Global styles are in `src/index.css` with:
- Custom CSS variables for theming
- Distill-specific utility classes
- Animation keyframes
- Responsive utilities

### Type Safety
Full TypeScript support with:
- Strict type checking
- Component prop interfaces
- Custom type definitions

## 🚀 Deployment

The site builds to a static `dist/` folder that can be deployed anywhere:

```bash
# Build for production
bun run build

# The dist/ folder contains your static site
```

### Deployment Options
- **GitHub Pages** - Perfect for open source projects
- **Netlify** - Easy deployment with form handling
- **Vercel** - Optimized for React applications
- **AWS S3 + CloudFront** - Scalable CDN deployment

## 📄 License

MIT License - Feel free to use this template for your own documentation sites.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions about the CIE framework, please visit the main repository.
For site-specific issues, please open an issue in this repository.