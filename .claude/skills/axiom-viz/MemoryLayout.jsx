import { useState } from 'react';

/**
 * Memory layout visualization for struct S { char a; double b; char c; }
 * Shows real padding waste (24 B) and the reordered form (16 B) that saves 8 B.
 */
export default function MemoryLayout() {
  const [mode, setMode] = useState('default'); // 'default' | 'reordered'

  const layouts = {
    default: {
      name: 'struct S { char a; double b; char c; };',
      size: 24,
      cells: [
        { start: 0,  len: 1, label: 'char a',   kind: 'field' },
        { start: 1,  len: 7, label: 'padding',  kind: 'pad' },
        { start: 8,  len: 8, label: 'double b', kind: 'field' },
        { start: 16, len: 1, label: 'char c',   kind: 'field' },
        { start: 17, len: 7, label: 'padding',  kind: 'pad' },
      ],
    },
    reordered: {
      name: 'struct S { double b; char a; char c; };',
      size: 16,
      cells: [
        { start: 0,  len: 8, label: 'double b', kind: 'field' },
        { start: 8,  len: 1, label: 'char a',   kind: 'field' },
        { start: 9,  len: 1, label: 'char c',   kind: 'field' },
        { start: 10, len: 6, label: 'padding',  kind: 'pad' },
      ],
    },
  };

  const layout = layouts[mode];
  const cellW = 56; // px per byte visualization
  const totalW = layout.size * cellW;

  return (
    <div>
      <div style={{display:'flex', alignItems:'center', gap:12, marginBottom:18}}>
        <div style={{fontFamily:'var(--font-mono)', fontSize:14, color:'var(--fg-2)', flex:1}}>
          {layout.name}
        </div>
        <div className="tabs" role="tablist">
          <button className={`tab-btn ${mode==='default'?'active':''}`} onClick={()=>setMode('default')}>As written ({layouts.default.size} B)</button>
          <button className={`tab-btn ${mode==='reordered'?'active':''}`} onClick={()=>setMode('reordered')}>Reordered ({layouts.reordered.size} B)</button>
        </div>
      </div>

      {/* Byte grid */}
      <div style={{overflowX:'auto', paddingBottom:8}}>
        <div style={{display:'flex', flexDirection:'column', gap:6, width: totalW}}>
          {/* Addresses */}
          <div style={{display:'flex', fontFamily:'var(--font-mono)', fontSize:11, color:'var(--fg-3)'}}>
            {Array.from({length: layout.size}).map((_, i) => (
              <div key={i} style={{width: cellW, textAlign:'center'}}>
                {i % 4 === 0 ? `0x${i.toString(16).padStart(2,'0')}` : ''}
              </div>
            ))}
          </div>
          {/* Cells */}
          <div style={{display:'flex', border:'1.5px solid var(--ink-700)', borderRadius:4, overflow:'hidden'}}>
            {layout.cells.map((c, i) => {
              const w = c.len * cellW;
              const isPad = c.kind === 'pad';
              return (
                <div
                  key={i}
                  style={{
                    width: w,
                    padding: '16px 14px',
                    background: isPad
                      ? 'repeating-linear-gradient(45deg, transparent 0 6px, var(--paper-200) 6px 12px)'
                      : (c.label.startsWith('double') ? 'var(--accent-50)'
                        : c.label.startsWith('char') ? '#edf4ee'
                        : '#fdf2ea'),
                    borderLeft: i === 0 ? 'none' : '1.5px solid var(--ink-700)',
                    fontFamily:'var(--font-mono)',
                    fontSize:14,
                    color: isPad ? 'var(--fg-3)' : 'var(--fg-1)',
                    fontStyle: isPad ? 'italic' : 'normal',
                    textAlign:'center',
                    display:'flex', flexDirection:'column', gap:4, alignItems:'center'
                  }}
                >
                  <div>{c.label}</div>
                  <div style={{fontSize:11, color:'var(--fg-3)'}}>{c.len} B</div>
                </div>
              );
            })}
          </div>
          {/* Byte ruler */}
          <div style={{display:'flex', fontFamily:'var(--font-mono)', fontSize:10, color:'var(--fg-4)'}}>
            {Array.from({length: layout.size}).map((_, i) => (
              <div key={i} style={{width: cellW, textAlign:'center', borderTop:'1px solid var(--border)', paddingTop:2}}>
                {i}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="narration">
        <span className="label">Observation</span>
        {mode === 'default'
          ? <>The <span className="code-inline">double</span> must sit on an 8-byte boundary, so 7 bytes of padding follow <span className="code-inline">char a</span>. Then the trailing <span className="code-inline">char c</span> forces another 7 bytes of tail padding — the struct rounds up to a multiple of 8. <strong>24 bytes total, 14 of them wasted.</strong></>
          : <>Put the widest field first. The two <span className="code-inline">char</span>s pack next to each other, and only 6 bytes of tail padding remain. <strong>16 bytes total — an 8-byte saving per instance,</strong> which matters in arrays of millions.</>
        }
      </div>
    </div>
  );
}
