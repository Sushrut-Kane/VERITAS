import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-col gap-4 border-b pb-6 sm:flex-row sm:flex-wrap sm:items-end sm:justify-between">
      <div>
        {eyebrow ? (
          <p className="data-value text-[11px] uppercase tracking-[0.24em] text-muted-foreground">{eyebrow}</p>
        ) : null}
        <h1 className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">{title}</h1>
        {description ? <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {actions}
    </div>
  );
}
