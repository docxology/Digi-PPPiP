# Local drawing demo

The React client in `web-app/client/` uses Vite. The Node.js server in `web-app/server/` relays drawing, undo, cursor, and presence events through Socket.IO. The demonstration uses a shared broadcast canvas. Use a local test environment and synthetic marks.

Install from each component's npm lockfile with `npm ci`. To preview the demo locally, run `node index.js` from `web-app/server/` and `npm run dev -- --host 127.0.0.1` from `web-app/client/`. Use an isolated local environment for the relay. The server defaults to port `3001`. The frontend defaults to port `5173` and connects to port `3001` on the page's hostname unless configured with `VITE_SERVER_URL`.

From the client directory, `npm run lint` checks source and `npm run build` generates `dist/`. Those commands do not start the server. The dashboard illustrates simulated free energy, synchrony, and entropy. The tracked screenshots illustrate the interface and serve as inputs to manuscript figure generation.
