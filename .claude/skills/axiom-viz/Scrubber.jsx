import { useEffect, useRef } from 'react';

/**
 * Reusable scrubber + play controls for walking through steps.
 * Props: step, total, onChange(step), playing, onTogglePlay, onReset
 */
export default function Scrubber({ step, total, onChange, playing, onTogglePlay, onReset, speed = 900 }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!playing) return;
    const id = setInterval(() => {
      onChange((step + 1) % total);
    }, speed);
    return () => clearInterval(id);
  }, [playing, step, total, speed, onChange]);

  function handleTrack(e) {
    const rect = ref.current.getBoundingClientRect();
    const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width));
    onChange(Math.round(ratio * (total - 1)));
  }

  const pct = total <= 1 ? 0 : (step / (total - 1)) * 100;
  return (
    <div className="controls">
      <button className="btn primary" onClick={onTogglePlay} aria-label={playing ? 'Pause' : 'Play'}>
        {playing ? (
          <svg className="ic" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        ) : (
          <svg className="ic" viewBox="0 0 24 24"><polygon points="6 3 20 12 6 21 6 3" fill="currentColor" stroke="none"/></svg>
        )}
        {playing ? 'Pause' : 'Play'}
      </button>
      <button className="btn" onClick={() => onChange(Math.max(0, step - 1))} disabled={step === 0}>
        <svg className="ic" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
      </button>
      <button className="btn" onClick={() => onChange(Math.min(total - 1, step + 1))} disabled={step === total - 1}>
        <svg className="ic" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
      <div className="scrubber">
        <div className="scrubber-track" ref={ref} onClick={handleTrack}>
          <div className="scrubber-fill" style={{width: `${pct}%`}} />
          <div className="scrubber-knob" style={{left: `${pct}%`}} />
        </div>
        <div className="counter">{step + 1} / {total}</div>
      </div>
      <button className="btn" onClick={onReset} title="Reset (R)">
        <svg className="ic" viewBox="0 0 24 24"><path d="M3 3v5h5"/><path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/></svg>
      </button>
    </div>
  );
}
