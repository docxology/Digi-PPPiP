import React, { useRef, useEffect, useState, useImperativeHandle, forwardRef } from 'react';

const Canvas = forwardRef(({ socket, userId, nickname, color, brushStyle, canvasBg, onDraw }, ref) => {
  const canvasRef = useRef(null);
  const contextRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);
  const [isDrawing, setIsDrawing] = useState(false);
  
  // Undo state tracking
  const segmentsRef = useRef([]);
  const currentStrokeIdRef = useRef(null);

  const redrawCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = contextRef.current;
    if (!ctx || !canvas) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Redraw all segments
    segmentsRef.current.forEach(seg => {
      ctx.beginPath();
      ctx.moveTo(seg.x0, seg.y0);
      ctx.lineTo(seg.x1, seg.y1);
      ctx.strokeStyle = seg.color;
      
      // Apply brush style
      if (seg.style === 'neon') {
        ctx.shadowBlur = 15;
        ctx.shadowColor = seg.color;
        ctx.setLineDash([]);
        ctx.lineWidth = 4;
      } else if (seg.style === 'dotted') {
        ctx.shadowBlur = 0;
        ctx.setLineDash([2, 10]);
        ctx.lineWidth = 6;
      } else {
        // Solid
        ctx.shadowBlur = 0;
        ctx.setLineDash([]);
        ctx.lineWidth = 4;
      }
      
      ctx.stroke();
      ctx.closePath();
      ctx.shadowBlur = 0; // Reset for next stroke
    });
  };

  useImperativeHandle(ref, () => ({
    undo: () => {
      // Find last stroke by this user
      const userSegments = segmentsRef.current.filter(s => s.userId === userId);
      if (userSegments.length === 0) return;
      
      const lastStrokeId = userSegments[userSegments.length - 1].strokeId;
      
      // Remove all segments with that strokeId
      segmentsRef.current = segmentsRef.current.filter(s => s.strokeId !== lastStrokeId);
      
      redrawCanvas();
      
      if (socket) {
        socket.emit('undo_stroke', { strokeId: lastStrokeId });
      }
    },
    exportPNG: () => {
      if (!canvasRef.current) return;
      
      const canvas = canvasRef.current;
      const exportCanvas = document.createElement('canvas');
      exportCanvas.width = canvas.width;
      exportCanvas.height = canvas.height;
      const ctx = exportCanvas.getContext('2d');
      
      if (canvasBg && canvasBg !== 'transparent') {
        ctx.fillStyle = canvasBg;
        ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);
      }
      
      ctx.drawImage(canvas, 0, 0);
      const dataUrl = exportCanvas.toDataURL('image/png');
      
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'digi-ppppip-canvas.png';
      a.click();
    },
    startRecording: () => {
      if (!canvasRef.current) return;
      recordedChunksRef.current = [];
      const stream = canvasRef.current.captureStream(30); // 30 fps
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'video/webm' });
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunksRef.current.push(e.data);
        }
      };
      mediaRecorderRef.current.start();
    },
    stopRecording: () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.onstop = () => {
          const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'digi-ppppip-session.webm';
          a.click();
          URL.revokeObjectURL(url);
        };
        mediaRecorderRef.current.stop();
      }
    }
  }));

  useEffect(() => {
    const canvas = canvasRef.current;
    
    // Set up canvas for high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    // We want the canvas to fill the screen
    const rect = canvas.parentElement.getBoundingClientRect();
    
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    
    const context = canvas.getContext('2d');
    context.scale(dpr, dpr);
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = 4;
    contextRef.current = context;

    // Handle window resize
    const handleResize = () => {
      const parentRect = canvas.parentElement.getBoundingClientRect();
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      
      canvas.width = parentRect.width * dpr;
      canvas.height = parentRect.height * dpr;
      context.scale(dpr, dpr);
      context.lineCap = 'round';
      context.lineJoin = 'round';
      
      context.putImageData(imageData, 0, 0);
      
      // Wait, during a resize the strokes would technically scale weirdly or get lost if we just putImageData.
      // Since we now store segments, we can actually just redraw!
      redrawCanvas();
    };

    window.addEventListener('resize', handleResize);
    
    // Listen for incoming remote drawing events
    if (socket) {
      socket.on('draw_path', (data) => {
        const { x0, y0, x1, y1, color: remoteColor, brushStyle: remoteStyle, strokeId, userId: remoteUserId } = data;
        drawOnCanvas(x0, y0, x1, y1, remoteColor, remoteStyle, strokeId, remoteUserId, false);
      });
      
      socket.on('undo_stroke', (data) => {
        segmentsRef.current = segmentsRef.current.filter(s => s.strokeId !== data.strokeId);
        redrawCanvas();
      });
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      if (socket) {
        socket.off('draw_path');
        socket.off('undo_stroke');
      }
    };
  }, [socket]);

  const drawOnCanvas = (x0, y0, x1, y1, strokeColor, style, strokeId, strokeUserId, emit = false) => {
    if (!contextRef.current) return;
    
    const ctx = contextRef.current;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.strokeStyle = strokeColor;
    
    // Apply brush style
    if (style === 'neon') {
      ctx.shadowBlur = 15;
      ctx.shadowColor = strokeColor;
      ctx.setLineDash([]);
      ctx.lineWidth = 4;
    } else if (style === 'dotted') {
      ctx.shadowBlur = 0;
      ctx.setLineDash([2, 10]);
      ctx.lineWidth = 6;
    } else {
      // Solid
      ctx.shadowBlur = 0;
      ctx.setLineDash([]);
      ctx.lineWidth = 4;
    }
    
    ctx.stroke();
    ctx.closePath();
    
    // Reset shadow so it doesn't leak
    ctx.shadowBlur = 0;

    // Track segment
    segmentsRef.current.push({
      x0, y0, x1, y1, color: strokeColor, style, strokeId, userId: strokeUserId
    });

    if (emit && socket) {
      socket.emit('draw_path', { x0, y0, x1, y1, color: strokeColor, brushStyle: style, strokeId, userId: strokeUserId });
    }
    
    if (emit && onDraw) {
      // Pass length of line for metrics calculation
      const dist = Math.sqrt(Math.pow(x1 - x0, 2) + Math.pow(y1 - y0, 2));
      onDraw(dist);
    }
  };

  const startDrawing = ({ nativeEvent }) => {
    const { offsetX, offsetY } = nativeEvent;
    
    // Generate a new stroke ID
    currentStrokeIdRef.current = Math.random().toString(36).substring(2, 15);
    
    // Set initial dot
    drawOnCanvas(offsetX, offsetY, offsetX, offsetY, color, brushStyle, currentStrokeIdRef.current, userId, true);
    setIsDrawing(true);
  };

  const finishDrawing = () => {
    setIsDrawing(false);
    currentStrokeIdRef.current = null;
  };

  const draw = ({ nativeEvent }) => {
    if (!isDrawing) {
      // Just track cursor if not drawing
      if (socket) {
        socket.emit('cursor_move', { x: nativeEvent.clientX, y: nativeEvent.clientY, nickname });
      }
      return;
    }
    
    const { offsetX, offsetY, movementX, movementY } = nativeEvent;
    const prevX = offsetX - movementX;
    const prevY = offsetY - movementY;
    
    drawOnCanvas(prevX, prevY, offsetX, offsetY, color, brushStyle, currentStrokeIdRef.current, userId, true);
    
    // Also emit cursor move while drawing
    if (socket) {
      socket.emit('cursor_move', { x: nativeEvent.clientX, y: nativeEvent.clientY, nickname });
    }
  };

  return (
    <canvas
      ref={canvasRef}
      aria-label="Shared drawing canvas. Click and drag to draw."
      role="img"
      onMouseDown={startDrawing}
      onMouseUp={finishDrawing}
      onMouseOut={finishDrawing}
      onMouseMove={draw}
      style={{
        width: '100%',
        height: '100%',
        backgroundColor: canvasBg === 'transparent' ? 'transparent' : canvasBg
      }}
    />
  );
});

export default Canvas;
