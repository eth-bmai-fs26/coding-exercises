const scenarios = [
  { key: 'conservative', label: 'Conservative', desc: 'Impact -30%, Costs +20%, Launch +2mo' },
  { key: 'base', label: 'Base', desc: 'As entered' },
  { key: 'optimistic', label: 'Optimistic', desc: 'Impact +25%, Costs -10%, Launch -1mo' },
];

export default function ScenarioTabs({ active, onChange }) {
  return (
    <div className="flex gap-2 mb-6">
      {scenarios.map((s) => (
        <button
          key={s.key}
          onClick={() => onChange(s.key)}
          className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all ${
            active === s.key
              ? 'bg-accent/15 text-accent border border-accent/40'
              : 'bg-dark-800 text-gray-400 border border-dark-700 hover:border-dark-500 hover:text-gray-300'
          }`}
          title={s.desc}
        >
          <span className="block">{s.label}</span>
          <span className={`block text-xs mt-0.5 ${active === s.key ? 'text-accent/70' : 'text-gray-600'}`}>
            {s.desc}
          </span>
        </button>
      ))}
    </div>
  );
}
