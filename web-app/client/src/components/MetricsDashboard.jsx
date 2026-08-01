import React, { useEffect, useState } from 'react';

const MetricsDashboard = ({ freeEnergy, ibs, entropy }) => {
  // We'll normalize these values to 0-100% for the progress bars
  
  // Free Energy: We want it to go down as couples synchronize (lower is better)
  // We'll display it so a lower FE is a smaller bar.
  const fePercent = Math.min(100, Math.max(0, (freeEnergy / 100) * 100));
  
  // Inter-brain Synchrony (IBS): Higher is better, max around 1.0
  const ibsPercent = Math.min(100, Math.max(0, ibs * 100));
  
  // Narrative Entropy: Varies, let's say max is 5 bits
  const entropyPercent = Math.min(100, Math.max(0, (entropy / 5) * 100));

  return (
    <div className="glass-panel metrics-dashboard" role="region" aria-label="Coupled dynamics metrics (illustrative simulation)">
      <div className="metrics-header">Coupled Dynamics</div>
      <p className="metrics-disclaimer">Simulated illustrative values — not measured clinical data.</p>
      
      <div className="metric-item">
        <div className="metric-header">
          <span>Variational Free Energy</span>
          <span className="metric-value">{freeEnergy.toFixed(2)}</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill fill-fe" style={{ width: `${fePercent}%` }}></div>
        </div>
      </div>

      <div className="metric-item">
        <div className="metric-header">
          <span>Inter-Brain Synchrony (IBS)</span>
          <span className="metric-value">{ibs.toFixed(2)}</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill fill-ibs" style={{ width: `${ibsPercent}%` }}></div>
        </div>
      </div>

      <div className="metric-item">
        <div className="metric-header">
          <span>Narrative Entropy (bits)</span>
          <span className="metric-value">{entropy.toFixed(2)}</span>
        </div>
        <div className="metric-bar-bg">
          <div className="metric-bar-fill fill-ent" style={{ width: `${entropyPercent}%` }}></div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;
