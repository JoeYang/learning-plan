export default function TopNav() {
  return (
    <div className="top">
      <div className="brand">
        <svg viewBox="0 0 48 48" fill="none">
          <g stroke="#171512" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 40 L24 8 L38 40"/><path d="M16 28 L32 28"/>
          </g>
        </svg>
        axiom
      </div>
      <div className="nav-links">
        <a href="#">Concepts</a>
        <a href="#" className="active">Visualizations</a>
        <a href="#">Notes</a>
      </div>
      <div className="spacer" />
      <div style={{display:'flex', alignItems:'center', gap:8, fontSize:13, color:'var(--fg-3)'}}>
        Search <span className="kbd">⌘K</span>
      </div>
    </div>
  );
}
