import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import Canvas from './components/Canvas';
import MetricsDashboard from './components/MetricsDashboard';
import './index.css';

// Socket server URL: override with VITE_SERVER_URL, otherwise fall back to the
// same host that serves the client on port 3001 (keeps local dev working).
const SERVER_URL = import.meta.env.VITE_SERVER_URL || `http://${window.location.hostname || 'localhost'}:3001`;

const COLORS = ['#00f0ff', '#8b5cf6', '#f43f5e', '#10b981', '#f59e0b'];
const THEMES = ['dark', 'light', 'comfort'];
const BRUSHES = ['solid', 'dotted', 'neon'];
const CANVAS_BGS = [
  { name: 'Transparent', value: 'transparent' },
  { name: 'Plain Black', value: '#000000' },
  { name: 'Plain White', value: '#ffffff' },
  { name: 'Warm Paper', value: '#fdf6e3' }
];
const ADJECTIVES = ['Silly', 'Spicy', 'Chonky', 'Grumpy', 'Sleepy', 'Derpy', 'Zesty', 'Sneaky', 'Bouncy', 'Funky', 'Hyper', 'Cozy', 'Majestic', 'Cheeky'];
const FRUITS = ['Banana', 'Mango', 'Kumquat', 'Papaya', 'Avocado', 'Kiwi', 'Pineapple', 'Watermelon', 'Peach', 'Lychee', 'Dragonfruit', 'Fig'];

function generateNickname() {
  const adj = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
  const fruit = FRUITS[Math.floor(Math.random() * FRUITS.length)];
  return `${adj} ${fruit}`;
}

function App() {
  const [socket, setSocket] = useState(null);
  const [partnerCount, setPartnerCount] = useState(0);
  const [myColor, setMyColor] = useState(COLORS[0]);
  const [theme, setTheme] = useState(THEMES[0]);
  const [brushStyle, setBrushStyle] = useState(BRUSHES[0]);
  const [canvasBg, setCanvasBg] = useState(CANVAS_BGS[0]);
  const [isRecording, setIsRecording] = useState(false);
  const [remoteCursors, setRemoteCursors] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const canvasRef = useRef(null);
  
  const [userId] = useState(() => Math.random().toString(36).substring(2, 15));
  const [nickname] = useState(() => generateNickname());

  useEffect(() => {
    document.title = `${nickname} | Digi-PPPiP`;
  }, [nickname]);
  
  // Digi-PPPiP Live Metrics State
  const [freeEnergy, setFreeEnergy] = useState(80.0);
  const [ibs, setIbs] = useState(0.1);
  const [entropy, setEntropy] = useState(2.0);

  useEffect(() => {
    // Connect to the local Socket.IO signaling server
    const newSocket = io(SERVER_URL, { reconnectionAttempts: 10 });
    setSocket(newSocket);

    newSocket.on('connect', () => setConnectionStatus('connected'));
    newSocket.on('disconnect', () => setConnectionStatus('disconnected'));
    newSocket.on('connect_error', () => setConnectionStatus('disconnected'));

    newSocket.on('partner_status', (data) => {
      setPartnerCount(data.partnerCount);
    });

    newSocket.on('cursor_move', (data) => {
      setRemoteCursors(prev => ({
        ...prev,
        [data.id]: { x: data.x, y: data.y, nickname: data.nickname }
      }));
    });

    newSocket.on('cursor_remove', (data) => {
      setRemoteCursors(prev => {
        const next = { ...prev };
        delete next[data.id];
        return next;
      });
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  useEffect(() => {
    const metricsInterval = setInterval(() => {
      setFreeEnergy(prev => {
        if (partnerCount > 0) {
          return Math.max(10, prev - (prev * 0.05));
        } else {
          return Math.min(100, prev + 2);
        }
      });
      
      setIbs(prev => {
        if (partnerCount > 0) {
          return Math.min(1.0, prev + 0.01 + Math.random() * 0.02);
        } else {
          return Math.max(0, prev - 0.02);
        }
      });
    }, 1000);

    return () => {
      clearInterval(metricsInterval);
    };
  }, [partnerCount]);

  const handleDraw = (strokeLength) => {
    setEntropy(prev => {
      const spike = strokeLength > 20 ? (strokeLength / 50) : -0.1;
      return Math.min(5.0, Math.max(0.1, prev + spike));
    });
  };

  const handleClear = () => {
    window.location.reload();
  };
  
  const handleUndo = () => {
    if (canvasRef.current) canvasRef.current.undo();
  };
  
  const handleExportPNG = () => {
    if (canvasRef.current) canvasRef.current.exportPNG();
  };
  
  const toggleRecording = () => {
    if (isRecording) {
      canvasRef.current.stopRecording();
      setIsRecording(false);
    } else {
      canvasRef.current.startRecording();
      setIsRecording(true);
    }
  };

  // Cycle through themes
  const toggleTheme = () => {
    const nextIndex = (THEMES.indexOf(theme) + 1) % THEMES.length;
    setTheme(THEMES[nextIndex]);
  };

  // Cycle through brush styles
  const toggleBrush = () => {
    const nextIndex = (BRUSHES.indexOf(brushStyle) + 1) % BRUSHES.length;
    setBrushStyle(BRUSHES[nextIndex]);
  };

  // Cycle through canvas backgrounds
  const toggleCanvasBg = () => {
    const nextIndex = (CANVAS_BGS.findIndex(bg => bg.value === canvasBg.value) + 1) % CANVAS_BGS.length;
    setCanvasBg(CANVAS_BGS[nextIndex]);
  };

  return (
    <div className={`app-container theme-${theme}`}>
      <div className="canvas-container">
        <Canvas 
          ref={canvasRef}
          socket={socket} 
          userId={userId}
          nickname={nickname}
          color={myColor} 
          brushStyle={brushStyle}
          canvasBg={canvasBg.value}
          onDraw={handleDraw} 
        />
      </div>

      {Object.entries(remoteCursors).map(([id, pos]) => (
        <div 
          key={id} 
          className="remote-cursor"
          style={{ left: pos.x, top: pos.y }}
        >
          <div className="cursor-dot"></div>
          <div className="cursor-label">{pos.nickname || 'Partner'}</div>
        </div>
      ))}

      <div className="ui-overlay">
        <div className="ui-header">
          <div className="glass-panel title-box">
            <h1>Digi-PPPiP</h1>
            <p>Digital Partner Pen Play in Parallel</p>
          </div>
          
          <div className="glass-panel status-badge" data-status={connectionStatus}>
            <div className="dot"></div>
            {connectionStatus === 'connected'
              ? (partnerCount > 0 ? 'Dyad Coupled' : 'Waiting for Partner...')
              : (connectionStatus === 'connecting' ? 'Connecting to server…' : 'Server offline')}
          </div>
        </div>

        <div className="glass-panel demo-note">
          <strong>Conceptual demo</strong> — illustrative visuals only; not a clinical or diagnostic tool.
        </div>

        <div className="glass-panel onboarding-hint">
          Click &amp; drag on the canvas to draw. Pick a color, brush, canvas background and theme below.
          Your session is identified as <strong className="nick">{nickname}</strong>.
        </div>

        <MetricsDashboard 
          freeEnergy={freeEnergy} 
          ibs={ibs} 
          entropy={entropy} 
        />

        <div className="glass-panel controls-panel" style={{ flexWrap: 'wrap', maxWidth: '800px' }}>
          <div className="color-picker" role="group" aria-label="Brush color">
            {COLORS.map(c => (
              <button
                key={c}
                aria-label={`Brush color ${c}`}
                aria-pressed={myColor === c}
                className={`color-btn ${myColor === c ? 'active' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => setMyColor(c)}
              />
            ))}
          </div>
          
          <button className="action-btn" onClick={toggleBrush} aria-label={`Brush style. Current: ${brushStyle}`}>
            Brush: {brushStyle.charAt(0).toUpperCase() + brushStyle.slice(1)}
          </button>
          
          <button className="action-btn" onClick={toggleCanvasBg} aria-label={`Canvas background. Current: ${canvasBg.name}`}>
            Canvas: {canvasBg.name}
          </button>
          
          <button className="action-btn" onClick={toggleTheme} aria-label={`Theme. Current: ${theme}`}>
            Theme: {theme.charAt(0).toUpperCase() + theme.slice(1)}
          </button>
          
          <button className="action-btn" onClick={handleExportPNG} aria-label="Save canvas as PNG">
            Save PNG
          </button>
          
          <button className={`action-btn ${isRecording ? 'recording' : ''}`} onClick={toggleRecording} style={isRecording ? {backgroundColor: 'var(--accent-pink)'} : {}} aria-label={isRecording ? 'Stop recording' : 'Start recording video'}>
            {isRecording ? 'Stop Recording' : 'Record Video'}
          </button>

          <button className="action-btn" onClick={handleUndo} aria-label="Undo last stroke">
            Undo
          </button>

          <button className="action-btn" onClick={handleClear} aria-label="Clear the canvas">
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
