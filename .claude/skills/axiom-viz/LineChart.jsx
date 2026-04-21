import { useState } from 'react';

/**
 * Interactive line chart comparing capacity growth strategies.
 * Hover-to-inspect. Uses viz palette.
 */
export default function LineChart() {
  const [hover, setHover] = useState(null);
  const n = 16;
  const xs = Array.from({length: n}, (_, i) => i + 1);

  const double = xs.map(i => {
    let cap = 1; while (cap < i) cap *= 2; return cap;
  });
  const onePointFive = xs.map(i => {
    let cap = 1; while (cap < i) cap = Math.ceil(cap * 1.5); return cap;
  });

  const W = 800, H = 360, padL = 60, padR = 20, padT = 30, padB = 40;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const maxY = Math.max(...double, ...onePointFive);

  const xPx = (i) => padL + (i / (n - 1)) * innerW;
  const yPx = (v) => padT + innerH - (v / maxY) * innerH;
  const pathFor = (data) =>
    data.map((v, i) => `${i === 0 ? 'M' : 'L'}${xPx(i)},${yPx(v)}`).join(' ');

  const ticks = [0, 64, 128, 192, 256];

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} style={{width:'100%', height:'auto'}}
           onMouseLeave={() => setHover(null)}>
        {ticks.map(t => (
          <g key={t}>
            <line x1={padL} y1={yPx(t)} x2={W-padR} y2={yPx(t)}
                  stroke="var(--viz-grid)" strokeWidth="1"/>
            <text x={padL-10} y={yPx(t)} textAnchor="end" dominantBaseline="central"
                  fontFamily="var(--font-sans)" fontSize="12" fill="var(--fg-3)">{t}</text>
          </g>
        ))}
        <line x1={padL} y1={padT} x2={padL} y2={H-padB} stroke="var(--viz-axis)" strokeWidth="1.5"/>
        <line x1={padL} y1={H-padB} x2={W-padR} y2={H-padB} stroke="var(--viz-axis)" strokeWidth="1.5"/>
        {[0, 4, 8, 12, 15].map(i => (
          <text key={i} x={xPx(i)} y={H-padB+18} textAnchor="middle"
                fontFamily="var(--font-sans)" fontSize="12" fill="var(--fg-3)">{xs[i]}</text>
        ))}
        <text x={padL + innerW/2} y={H-4} textAnchor="middle"
              fontFamily="var(--font-sans)" fontSize="12" fill="var(--fg-3)">pushes</text>
        <text x={16} y={padT + innerH/2} textAnchor="middle" transform={`rotate(-90, 16, ${padT + innerH/2})`}
              fontFamily="var(--font-sans)" fontSize="12" fill="var(--fg-3)">capacity</text>

        <path d={pathFor(double)} fill="none" stroke="var(--viz-1)" strokeWidth="2.5"/>
        <path d={pathFor(onePointFive)} fill="none" stroke="var(--viz-2)" strokeWidth="2.5" strokeDasharray="5 5"/>

        {xs.map((_, i) => (
          <rect key={i} x={xPx(i)-14} y={padT} width={28} height={innerH} fill="transparent"
                onMouseEnter={() => setHover(i)}/>
        ))}
        {hover != null && (
          <>
            <line x1={xPx(hover)} y1={padT} x2={xPx(hover)} y2={H-padB}
                  stroke="var(--fg-3)" strokeWidth="1" strokeDasharray="3 3"/>
            <circle cx={xPx(hover)} cy={yPx(double[hover])} r="5" fill="var(--viz-1)"/>
            <circle cx={xPx(hover)} cy={yPx(onePointFive[hover])} r="5" fill="var(--viz-2)"/>
            <g transform={`translate(${Math.min(xPx(hover)+12, W-padR-160)}, ${padT+8})`}>
              <rect width="150" height="64" fill="#fff" stroke="var(--border)" rx="4"/>
              <text x="10" y="18" fontFamily="var(--font-sans)" fontSize="12" fill="var(--fg-3)">After push #{xs[hover]}</text>
              <circle cx="14" cy="34" r="4" fill="var(--viz-1)"/>
              <text x="24" y="38" fontFamily="var(--font-mono)" fontSize="12" fill="var(--fg-1)">×2: {double[hover]}</text>
              <circle cx="14" cy="52" r="4" fill="var(--viz-2)"/>
              <text x="24" y="56" fontFamily="var(--font-mono)" fontSize="12" fill="var(--fg-1)">×1.5: {onePointFive[hover]}</text>
            </g>
          </>
        )}

        <g transform={`translate(${W-padR-200}, ${padT-10})`}>
          <circle cx="0" cy="0" r="5" fill="var(--viz-1)"/>
          <text x="12" y="4" fontFamily="var(--font-sans)" fontSize="13" fill="var(--fg-1)">libc++ · ×2</text>
          <circle cx="100" cy="0" r="5" fill="var(--viz-2)"/>
          <text x="112" y="4" fontFamily="var(--font-sans)" fontSize="13" fill="var(--fg-1)">MSVC · ×1.5</text>
        </g>
      </svg>
      <div className="narration">
        <span className="label">Read this chart</span>
        Both strategies amortize to O(1) per push, but ×2 reaches high capacities in fewer reallocations — at the cost of up to 2× wasted memory after the last growth. Hover the chart to inspect individual values.
      </div>
    </div>
  );
}
