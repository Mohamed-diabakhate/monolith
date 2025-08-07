import { ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl bg-white/70 dark:bg-gray-900/60 shadow-sm ring-1 ring-black/5 backdrop-blur supports-[backdrop-filter]:bg-white/60 ${className}`}
    >
      {children}
    </div>
  );
}

export function CardBody({
  children,
  className = "p-4",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={className}>{children}</div>;
}

export function StatCard({
  title,
  value,
  sub,
}: {
  title: string;
  value: string;
  sub?: string;
}) {
  return (
    <Card>
      <CardBody>
        <div className="text-xs uppercase tracking-wide text-gray-500">
          {title}
        </div>
        <div className="mt-1 text-2xl font-bold">{value}</div>
        {sub ? <div className="mt-1 text-xs text-gray-500">{sub}</div> : null}
      </CardBody>
    </Card>
  );
}
