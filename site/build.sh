#!/bin/bash
set -e

echo "Building CIE Documentation Site..."

# Navigate to site directory
cd "$(dirname "$0")"

# Type check
echo "Running TypeScript check..."
bunx tsc --noEmit

# Build with Vite
echo "Building with Vite..."
bunx vite build --outDir dist

echo "Build completed successfully!"
echo "Output directory: dist/"