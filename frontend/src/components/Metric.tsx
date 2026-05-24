interface MetricProps {
  label: string;
  value: string | number;
}

export function Metric({ label, value }: MetricProps) {
  return (
    <article className="metric">
      <span className="muted">{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
