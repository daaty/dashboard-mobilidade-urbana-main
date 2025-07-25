// Basic Progress component for UI
export function Progress({ value = 0, max = 100, ...props }) {
  return (
    <div className="w-full bg-gray-200 rounded h-2" {...props}>
      <div
        className="bg-blue-600 h-2 rounded"
        style={{ width: `${(value / max) * 100}%` }}
      />
    </div>
  );
}
