import React from 'react'

export function Select({ value, onChange, children, className = '', ...props }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className={`border rounded px-3 py-2 bg-white dark:bg-gray-900 text-gray-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
      {...props}
    >
      {children}
    </select>
  )
}

export function SelectOption({ value, children }) {
  return <option value={value}>{children}</option>
}
