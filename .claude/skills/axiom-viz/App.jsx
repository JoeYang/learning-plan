import TopNav from './TopNav.jsx';
import VizCard from './VizCard.jsx';
import MemoryLayout from './MemoryLayout.jsx';
import TreeTraversal from './TreeTraversal.jsx';
import LineChart from './LineChart.jsx';

export default function App() {
  return (
    <>
      <TopNav />

      <div className="page-head">
        <div className="eyebrow">Lecture 04 · Systems</div>
        <h1>Memory, trees, and growth</h1>
        <div className="lead">Three interactive figures from this week's readings. Step through them at your own pace.</div>
      </div>

      <VizCard title="Memory layout & padding" fig="Fig. 1"
               foot="Toggle reordered variant. Highlighted cells are fields; hatched cells are padding.">
        <MemoryLayout />
      </VizCard>

      <VizCard title="DFS on a binary tree" fig="Fig. 2"
               foot="Pre-order traversal. Play to animate; drag the scrubber to inspect any step.">
        <TreeTraversal />
      </VizCard>

      <VizCard title="Capacity growth — ×2 vs ×1.5" fig="Fig. 3"
               foot="Hover to inspect capacity after each push. Both are amortized O(1).">
        <LineChart />
      </VizCard>
    </>
  );
}
