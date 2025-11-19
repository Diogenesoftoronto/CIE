# Web Development Guide

This guide covers the technology stack and development patterns for the CIE website located in the `site/` directory.

## Technology Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Runtime/Package Manager**: Bun
- **Language**: TypeScript

## Directory Structure

```
site/
├── src/
│   ├── components/     # React components (Hero, Architecture, etc.)
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   ├── App.tsx         # Main application component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── index.html          # HTML entry point
└── package.json        # Dependencies and scripts
```

## Development Workflow

### Installation

```bash
cd site
bun install
```

### Development Server

To start the local development server:

```bash
bun run dev
```

### Building for Production

To build the static site:

```bash
bun run build
```

The output will be in the `dist/` directory.

## Key Components

- **Hero.tsx**: The landing section, highlighting the project's value proposition.
- **Architecture.tsx**: Interactive diagram explaining the system layers (UI, Context, Backend, etc.).
- **InteractiveDemo.tsx**: A simulation of the optimization process with real-time metrics.
- **Introduction.tsx**: Problem statement and solution overview.

## Styling Patterns

The project uses Tailwind CSS for styling. Common patterns include:

- **Gradients**: `bg-gradient-to-br from-slate-50 to-slate-200` for backgrounds.
- **Cards**: `bg-white rounded-xl p-8 shadow-lg` for content containers.
- **Text**: `text-slate-900` for headings, `text-slate-600` for body text.
- **Interactive Elements**: `hover:scale-105 transition-all duration-200` for buttons and cards.

## Recent Updates

- **Harlequin TUI Integration**: The website content has been updated to reflect the new Harlequin-inspired TUI and Prompts panel.
- **Bun Migration**: The project now explicitly uses `bun` for package management and scripts.
