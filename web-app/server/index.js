const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

let connections = 0;

io.on('connection', (socket) => {
  connections++;
  console.log(`User connected: ${socket.id} (Total: ${connections})`);

  // Inform the new user of their partner status
  socket.emit('partner_status', { partnerCount: connections - 1 });
  // Inform others
  socket.broadcast.emit('partner_status', { partnerCount: connections - 1 });

  // Handle drawing paths
  socket.on('draw_path', (data) => {
    socket.broadcast.emit('draw_path', data);
  });
  
  // Handle undo
  socket.on('undo_stroke', (data) => {
    socket.broadcast.emit('undo_stroke', data);
  });

  // Handle cursor positions
  socket.on('cursor_move', (data) => {
    socket.broadcast.emit('cursor_move', {
      id: socket.id,
      ...data
    });
  });

  socket.on('disconnect', () => {
    connections--;
    console.log(`User disconnected: ${socket.id} (Total: ${connections})`);
    socket.broadcast.emit('partner_status', { partnerCount: connections - 1 });
    socket.broadcast.emit('cursor_remove', { id: socket.id });
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Socket.io server running on port ${PORT}`);
});
