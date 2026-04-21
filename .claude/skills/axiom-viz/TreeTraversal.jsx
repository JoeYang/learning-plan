import { useState, useMemo } from 'react';
import Scrubber from './Scrubber.jsx';

/**
 * Tree traversal visualization — DFS on a binary tree.
 * Steps through visiting each node, highlighting current + visited nodes
 * and edges traversed.
 */

// Tree structure:
//         1
//        / \
//       2   5
//      / \ / \
//     3  4 6  7
const NODES = [
  { id: 1, x: 300, y: 40  },
  { id: 2, x: 180, y: 110 },
  { id: 3, x: 110, y: 180 },
  { id: 4, x: 250, y: 180 },
  { id: 5, x: 420, y: 110 },
  { id: 6, x: 350, y: 180 },
  { id: 7, x: 490, y: 180 },
];
const EDGES = [
  { from: 1, to: 2 }, { from: 1, to: 5 },
  { from: 2, to: 3 }, { from: 2, to: 4 },
  { from: 5, to: 6 }, { from: 5, to: 7 },
];
// DFS pre-order visit sequence (by node id).
const DFS_SEQ = [1, 2, 3, 4, 5, 6, 7];

export default function TreeTraversal() {
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const total = DFS_SEQ.length;

  const visited = useMemo(() => new Set(DFS_SEQ.slice(0, step + 1)), [step]);
  const current = DFS_SEQ[step];
  const stack = useMemo(() => {
    const parent = { 1: null, 2: 1, 3: 2, 4: 2, 5: 1, 6: 5, 7: 5 };
    const path = [];
    let n = current;
    while (n != null) { path.unshift(n); n = parent[n]; }
    return path;
  }, [current]);

  const nodeById = (id) => NODES.find(n => n.id === id);

  return (
    <div>
      <div style={{display:'grid', gridTemplateColumns:'1fr 240px', gap:24, alignItems:'stretch'}}>
        <div>
          <svg viewBox="0 0 600 220" style={{width:'100%', height:'auto', background:'var(--bg-sunken)', border:'1px solid var(--border)', borderRadius:6}}>
            {EDGES.map((e, i) => {
              const a = nodeById(e.from);
              const b = nodeById(e.to);
              const active = visited.has(e.from) && visited.has(e.to);
              return (
                <line key={i}
                  x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                  stroke={active ? 'var(--accent-500)' : 'var(--ink-700)'}
                  strokeWidth={active ? 2 : 1.5}
                />
              );
            })}
            {NODES.map(n => {
              const isCurrent = n.id === current;
              const isVisited = visited.has(n.id) && !isCurrent;
              const fill = isCurrent ? 'var(--accent-500)' : isVisited ? 'var(--accent-50)' : '#fff';
              const stroke = isCurrent || isVisited ? 'var(--accent-500)' : 'var(--ink-700)';
              const textFill = isCurrent ? '#fff' : 'var(--fg-1)';
              return (
                <g key={n.id}>
                  <circle cx={n.x} cy={n.y} r={18} fill={fill} stroke={stroke} strokeWidth={1.5} />
                  <text x={n.x} y={n.y} textAnchor="middle" dominantBaseline="central"
                    fontFamily="var(--font-mono)" fontSize="14" fill={textFill}>
                    {n.id}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>

        <div style={{background:'var(--bg-sunken)', border:'1px solid var(--border)', borderRadius:6, padding:16, display:'flex', flexDirection:'column'}}>
          <div style={{fontSize:11, letterSpacing:'0.08em', textTransform:'uppercase', color:'var(--fg-3)', marginBottom:10, fontWeight:500}}>Call stack</div>
          <div style={{display:'flex', flexDirection:'column-reverse', gap:4, flex:1, justifyContent:'flex-start'}}>
            {stack.map((id, i) => (
              <div key={id} style={{
                fontFamily:'var(--font-mono)', fontSize:13,
                padding:'8px 12px',
                background: i === stack.length - 1 ? 'var(--accent-500)' : '#fff',
                color: i === stack.length - 1 ? '#fff' : 'var(--fg-1)',
                border:'1px solid var(--border)',
                borderRadius:4,
              }}>
                dfs({id})
              </div>
            ))}
          </div>
          <div style={{fontSize:11, color:'var(--fg-3)', marginTop:10, fontFamily:'var(--font-mono)'}}>
            visited: [{DFS_SEQ.slice(0, step+1).join(', ')}]
          </div>
        </div>
      </div>

      <Scrubber
        step={step}
        total={total}
        onChange={setStep}
        playing={playing}
        onTogglePlay={() => setPlaying(p => !p)}
        onReset={() => { setStep(0); setPlaying(false); }}
      />

      <div className="narration">
        <span className="label">Step {step + 1}</span>
        {step === 0 && <>Enter DFS at the root. We push <span className="code-inline">dfs(1)</span> onto the call stack and visit node 1.</>}
        {step === 1 && <>Recurse into the left child. <span className="code-inline">dfs(2)</span> is pushed; node 2 is visited.</>}
        {step === 2 && <>Descend further left. Node 3 is a leaf — we visit it, then return.</>}
        {step === 3 && <>Back in <span className="code-inline">dfs(2)</span>, recurse right. Node 4 is visited.</>}
        {step === 4 && <>Unwind to <span className="code-inline">dfs(1)</span> and recurse right. Node 5 is visited.</>}
        {step === 5 && <>Descend left of 5. Node 6 is a leaf — visit, return.</>}
        {step === 6 && <>Final leaf on the right. Node 7 completes the pre-order traversal.</>}
      </div>
    </div>
  );
}
