import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import Canvas from './components/Canvas';
import MetricsDashboard from './components/MetricsDashboard';
import './index.css';

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
    // Connect to local Node server
    const newSocket = io('http://localhost:3001');
    setSocket(newSocket);

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
          
          <div className={`glass-panel status-badge ${partnerCount > 0 ? 'connected' : 'waiting'}`}>
            <div className="dot"></div>
            {partnerCount > 0 ? 'Dyad Coupled' : 'Waiting for Partner...'}
          </div>
        </div>

        <MetricsDashboard 
          freeEnergy={freeEnergy} 
          ibs={ibs} 
          entropy={entropy} 
        />

        <div className="glass-panel controls-panel" style={{ flexWrap: 'wrap', maxWidth: '800px' }}>
          <div className="color-picker">
            {COLORS.map(c => (
              <button
                key={c}
                className={`color-btn ${myColor === c ? 'active' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => setMyColor(c)}
              />
            ))}
          </div>
          
          <button className="action-btn" onClick={toggleBrush}>
            Brush: {brushStyle.charAt(0).toUpperCase() + brushStyle.slice(1)}
          </button>
          
          <button className="action-btn" onClick={toggleCanvasBg}>
            Canvas: {canvasBg.name}
          </button>
          
          <button className="action-btn" onClick={toggleTheme}>
            Theme: {theme.charAt(0).toUpperCase() + theme.slice(1)}
          </button>
          
          <button className="action-btn" onClick={handleExportPNG}>
            Save PNG
          </button>
          
          <button className={`action-btn ${isRecording ? 'recording' : ''}`} onClick={toggleRecording} style={isRecording ? {backgroundColor: 'var(--accent-pink)'} : {}}>
            {isRecording ? 'Stop Recording' : 'Record Video'}
          </button>

          <button className="action-btn" onClick={handleUndo}>
            Undo
          </button>

          <button className="action-btn" onClick={handleClear}>
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
