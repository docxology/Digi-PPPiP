# Digi-PPPiP Server

The backend signaling server for **Digital Partner Pen Play in Parallel**. This Node.js/Express application provides the low-latency WebSocket backbone required to synchronize dyadic play.

## 📡 Overview

Because Digi-PPPiP relies on real-time drawing and rapid visual synchronization to instantiate Inter-Brain Synchronization (IBS), it utilizes `Socket.IO` over WebSockets to ensure that continuous mouse movements and stroke data are transmitted between partners as fast as possible. 

This server acts as a thin, stateless orchestrator. It does not persist drawing data to a database; instead, it rapidly relays incoming messages to all connected peers in real-time.

### Handled Events
- `connection` / `disconnect`: Maintains the global connection pool. Broadcasts the `partner_status` event to active clients so the frontend metrics loop can track the system's coupling state (isolated vs. coupled).
- `cursor_move`: Relays the precise `(x, y)` coordinates and `Adjective-Fruit` nickname of a user to all partners, driving the glowing remote cursor UI.
- `draw_path`: Relays vector drawing segments (coordinates, stroke width, color, and brush style) so that peers see identical ink strokes instantly.
- `undo_stroke`: Transmits the unique `strokeId` of an undone action, commanding peer clients to erase that specific stroke segment from their local canvas memory to maintain perfect sync without disrupting other drawings.

## 🚀 Development

### Prerequisites
- [Node.js](https://nodejs.org/) v18+

### Setup
```bash
# Install dependencies
npm install

# Start the Node.js server
node index.js
```

### Production Deployment
The server binds to port `3001` by default, but it will respect the `PORT` environment variable if provided by a cloud hosting provider (e.g., Render, Railway, or Heroku). 

The following environment variables tune the server's hardening knobs:

- `CORS_ORIGIN` — comma-separated allowed origins (default: `http://localhost:3000`). Set this to the explicit origin hosting your Vite client before any non-local deployment.
- `MAX_CONNECTIONS` — hard cap on concurrent sockets (default: `100`). When exceeded, new clients receive a `server_full` event and are disconnected.
- `RATE_LIMIT` — per-socket broadcast allowance per second via a token bucket (default: `240` events/sec). `RATE_LIMIT_ENABLED=false` disables throttling for trusted/private networks.
- `PORT` — listening port (default: `3001`).

The server accepts no drawing data by default: `draw_path`, `undo_stroke`, and
`cursor_move` payloads are size-capped at 64 KiB, and Socket.IO's
`maxHttpBufferSize` is pinned to the same 64 KiB to bound per-frame memory.

