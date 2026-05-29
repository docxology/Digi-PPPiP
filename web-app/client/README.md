# Digi-PPPiP Client

The frontend application for **Digital Partner Pen Play in Parallel**. This React/Vite application provides the high-performance visualization surface for dyadic coupled active inference.

## 🎨 Overview

This client is responsible for rendering the shared digital canvas, maintaining the state of the interactive UI (glassmorphism overlay, brush/theme selectors), and dynamically simulating the theoretical metrics of the Digi-PPPiP framework based on real-time inputs.

### Core Components
- **`App.jsx`**: The orchestrator. It manages the `Socket.IO` connection lifecycle, captures `partnerCount` dynamically, triggers the neuroergodynamic metric simulation loop, and assigns playful `Adjective-Fruit` identities to users.
- **`Canvas.jsx`**: A high-DPI HTML5 canvas integration. It bypasses the React virtual DOM for drawing operations, storing vector line segments natively in memory. It is responsible for low-latency path rendering, handling `Undo` state, capturing remote cursors, and generating PNG/WebM exports.
- **`MetricsDashboard.jsx`**: The readout for Variational Free Energy, Inter-Brain Synchronization (IBS), and Narrative Entropy.

## 🚀 Development

### Prerequisites
- [Node.js](https://nodejs.org/) v18+

### Setup
```bash
# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

### Production Build
```bash
npm run build
```
This command compiles the React application into static files within the `dist/` directory, which can be deployed to any static host (e.g., Vercel, Netlify, GitHub Pages).

## 🔌 Connection to Server
By default, the client expects the Socket.IO server to be running locally at `http://localhost:3001`. If you are deploying this application, update the connection URI in `App.jsx` to point to your live server endpoint.
