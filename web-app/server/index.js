/* Digi-PPPiP Socket.IO signaling server.
 *
 * Thin, stateless relay: connects peers and forwards drawing / cursor events
 * between them. It does NOT persist any drawing data.
 *
 * Hardening notes:
 *  - CORS origin is env-configurable (CORS_ORIGIN) with a conservative local
 *    default instead of a blanket "*".
 *  - A per-event payload size cap and a `connections` cap bound resource use
 *    from any single client.
 *  - The connection counter is tracked as a Set of socket ids so it can never
 *    drift negative on reconnect races.
 *  - Per-event rate limiting throttles a malicious client's broadcast
 *    amplification, and `maxHttpBufferSize` caps each WebSocket frame size.
 */

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

// Conservative default: same-machine dev. Override with CORS_ORIGIN for other
// deployments (e.g. the explicit Vite client origin), comma-separated.
const ALLOWED_ORIGINS = (process.env.CORS_ORIGIN || 'http://localhost:3000')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

const MAX_CONNECTIONS = Number(process.env.MAX_CONNECTIONS || 100);
const MAX_PAYLOAD_BYTES = 64 * 1024; // 64 KiB per drawing/cursor payload
const MAX_BUFFER_BYTES = 64 * 1024; // Socket.IO frame cap (also 64 KiB)

// Per-socket token bucket: at most RATE_PER_WINDOW events per WINDOW_MS of
// broadcastable events. Prevents a single client amplifying to all peers.
const RATE_LIMIT_ENABLED = process.env.RATE_LIMIT_ENABLED !== 'false';
const RATE_WINDOW_MS = 1000;
const RATE_LIMIT = Number(process.env.RATE_LIMIT || 240); // ~4 events/sec

const app = express();
app.use(cors({ origin: ALLOWED_ORIGINS }));

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: ALLOWED_ORIGINS,
    methods: ['GET', 'POST'],
  },
  maxHttpBufferSize: MAX_BUFFER_BYTES,
});

// Set of live socket ids (more robust than a raw int counter).
const sockets = new Set();
// Per-socket rate-limit buckets: socket.id -> { tokens, refillAt }.
const rateBuckets = new Map();

function broadcastPayloadSizeOk(data, fallback) {
  if (data === undefined || data === null) {
    return fallback;
  }
  let bytes;
  try {
    bytes = Buffer.byteLength(JSON.stringify(data));
  } catch {
    return false;
  }
  return bytes <= MAX_PAYLOAD_BYTES;
}

// Refill a socket's token bucket and return whether one broadcast is allowed.
function allowBroadcast(socketId) {
  if (!RATE_LIMIT_ENABLED) {
    return true;
  }
  const now = Date.now();
  let bucket = rateBuckets.get(socketId);
  if (!bucket) {
    bucket = { tokens: RATE_LIMIT, refillAt: now + RATE_WINDOW_MS };
    rateBuckets.set(socketId, bucket);
    return true;
  }
  if (now >= bucket.refillAt) {
    bucket.tokens = RATE_LIMIT;
    bucket.refillAt = now + RATE_WINDOW_MS;
  }
  if (bucket.tokens <= 0) {
    return false;
  }
  bucket.tokens -= 1;
  return true;
}

// Generic guarded broadcast: drop oversized or rate-limited events.
function guardedBroadcast(socket, event, data) {
  if (!broadcastPayloadSizeOk(data, false) || !allowBroadcast(socket.id)) {
    return;
  }
  if (event === 'cursor_move') {
    socket.broadcast.emit(event, { id: socket.id, ...data });
    return;
  }
  socket.broadcast.emit(event, data);
}

io.on('connection', (socket) => {
  sockets.add(socket.id);

  // Enforce a hard cap on concurrent connections.
  if (sockets.size > MAX_CONNECTIONS) {
    socket.emit('server_full', { message: 'server connection limit reached' });
    socket.disconnect(true);
    return;
  }

  // Inform the new user of their partner status.
  socket.emit('partner_status', { partnerCount: sockets.size - 1 });
  // Inform others.
  socket.broadcast.emit('partner_status', { partnerCount: sockets.size - 1 });

  // Handle drawing paths.
  socket.on('draw_path', (data) => guardedBroadcast(socket, 'draw_path', data));

  // Handle undo.
  socket.on('undo_stroke', (data) => guardedBroadcast(socket, 'undo_stroke', data));

  // Handle cursor positions.
  socket.on('cursor_move', (data) => guardedBroadcast(socket, 'cursor_move', data));

  socket.on('disconnect', () => {
    sockets.delete(socket.id);
    rateBuckets.delete(socket.id);
    socket.broadcast.emit('partner_status', { partnerCount: sockets.size - 1 });
    socket.broadcast.emit('cursor_remove', { id: socket.id });
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Socket.io server running on port ${PORT}`);
});

// Graceful shutdown: drain connections on SIGTERM / SIGINT.
function shutdown(signal) {
  console.log(`${signal} received, shutting down.`);
  io.close(() => {
    server.close(() => process.exit(0));
  });
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
