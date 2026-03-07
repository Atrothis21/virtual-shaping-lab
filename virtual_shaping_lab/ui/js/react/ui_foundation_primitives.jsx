window.VSLReact = window.VSLReact || {};

function PageRegion({ className, children }) {
  const extra = className ? ` ${className}` : "";
  return <section className={`vsl-page-region${extra}`}>{children}</section>;
}

function SurfacePanel({ className, children }) {
  const extra = className ? ` ${className}` : "";
  return <div className={`vsl-surface-panel${extra}`}>{children}</div>;
}

function StatusBadge({ tone, className, children }) {
  const safeTone = tone || "default";
  const extra = className ? ` ${className}` : "";
  return <span className={`vsl-status-badge ${safeTone}${extra}`}>{children}</span>;
}

function PrimaryButton({ onClick, children, disabled, className }) {
  const extra = className ? ` ${className}` : "";
  return (
    <button type="button" disabled={disabled} className={`vsl-btn vsl-btn-primary${extra}`} onClick={onClick}>
      {children}
    </button>
  );
}

function SecondaryButton({ onClick, children, disabled, className }) {
  const extra = className ? ` ${className}` : "";
  return (
    <button type="button" disabled={disabled} className={`vsl-btn vsl-btn-secondary${extra}`} onClick={onClick}>
      {children}
    </button>
  );
}

window.VSLReact.foundationPrimitives = {
  PageRegion,
  SurfacePanel,
  StatusBadge,
  PrimaryButton,
  SecondaryButton,
};
