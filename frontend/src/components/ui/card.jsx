// Basic Card component for UI
export function Card({ children, ...props }) {
  return <div className="bg-white rounded shadow p-4" {...props}>{children}</div>;
}

export function CardHeader({ children, ...props }) {
  return <div className="border-b pb-2 mb-2 font-bold text-lg" {...props}>{children}</div>;
}

export function CardTitle({ children, ...props }) {
  return <div className="text-xl font-semibold mb-1" {...props}>{children}</div>;
}

export function CardContent({ children, ...props }) {
  return <div className="py-2" {...props}>{children}</div>;
}
