// Basic Label component for UI
export function Label({ children, ...props }) {
  return <label className="block text-sm font-medium text-gray-700 mb-1" {...props}>{children}</label>;
}
