// Basic Alert component for UI
export function Alert({ children, type = 'info', ...props }) {
  const color = type === 'error' ? 'bg-red-100 text-red-700' : type === 'success' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700';
  return (
    <div className={`p-3 rounded ${color}`} {...props}>
      {children}
    </div>
  );
}

export function AlertDescription({ children, ...props }) {
  return <div className="text-sm text-gray-600 mt-1" {...props}>{children}</div>;
}
