// Basic Tabs component for UI
import { useState } from 'react';

export function Tabs({ tabs = [], defaultIndex = 0 }) {
  const [active, setActive] = useState(defaultIndex);
  return (
    <div>
      <div className="flex border-b mb-2">
        {tabs.map((tab, idx) => (
          <button
            key={tab.label}
            className={`px-4 py-2 -mb-px border-b-2 ${active === idx ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600'}`}
            onClick={() => setActive(idx)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>{tabs[active]?.content}</div>
    </div>
  );
}
