export default function VizCard({ fig, title, children, foot }) {
  return (
    <div className="viz-card">
      <div className="viz-head">
        <div className="title">{title}</div>
        <div className="fig">{fig}</div>
      </div>
      <div className="viz-body">{children}</div>
      {foot ? <div className="viz-foot">{foot}</div> : null}
    </div>
  );
}
