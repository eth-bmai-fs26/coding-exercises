import { useState } from 'react';

const PARAM_CONFIG = {
  revenueModel: { label: 'Revenue Model', type: 'select', options: ['new_revenue', 'churn_reduction', 'cost_savings'], display: { new_revenue: 'New Revenue', churn_reduction: 'Churn Reduction', cost_savings: 'Cost Savings' } },
  baseCustomers: { label: 'Base Customers', type: 'number', unit: '', min: 0, step: 10 },
  growthRate: { label: 'Monthly Growth Rate', type: 'percent', min: -0.5, max: 1, step: 0.01 },
  revenuePerCustomer: { label: 'Revenue per Customer', type: 'currency', min: 0, step: 10 },
  subscriberBase: { label: 'Subscriber Base', type: 'number', unit: '', min: 0, step: 1000 },
  oldChurn: { label: 'Current Churn Rate', type: 'percent', min: 0, max: 1, step: 0.005 },
  newChurn: { label: 'Target Churn Rate', type: 'percent', min: 0, max: 1, step: 0.005 },
  avgRevenuePerUser: { label: 'Avg Revenue per User', type: 'currency', min: 0, step: 5 },
  currentMonthlyCost: { label: 'Current Monthly Cost', type: 'currency', min: 0, step: 5000 },
  savingsPercentage: { label: 'Savings Rate', type: 'percent', min: 0, max: 1, step: 0.05 },
  fixedMonthlyCost: { label: 'Fixed Monthly Cost', type: 'currency', min: 0, step: 1000 },
  variableRate: { label: 'Variable Cost Rate', type: 'percent', min: 0, max: 1, step: 0.01 },
  upfrontCost: { label: 'Upfront Investment', type: 'currency', min: 0, step: 5000 },
  launchMonth: { label: 'Launch Month', type: 'number', unit: 'month', min: 1, max: 24, step: 1 },
  startingBudget: { label: 'Starting Budget', type: 'currency', min: 0, step: 10000 },
};

// Which params are relevant for each revenue model
const MODEL_PARAMS = {
  new_revenue: ['revenueModel', 'baseCustomers', 'growthRate', 'revenuePerCustomer', 'fixedMonthlyCost', 'variableRate', 'upfrontCost', 'launchMonth', 'startingBudget'],
  churn_reduction: ['revenueModel', 'subscriberBase', 'oldChurn', 'newChurn', 'avgRevenuePerUser', 'fixedMonthlyCost', 'variableRate', 'upfrontCost', 'launchMonth', 'startingBudget'],
  cost_savings: ['revenueModel', 'currentMonthlyCost', 'savingsPercentage', 'fixedMonthlyCost', 'variableRate', 'upfrontCost', 'launchMonth', 'startingBudget'],
};

function formatValue(value, config) {
  if (config.type === 'percent') return `${(value * 100).toFixed(1)}%`;
  if (config.type === 'currency') return `CHF ${Number(value).toLocaleString()}`;
  if (config.type === 'select') return config.display?.[value] || value;
  return `${value}${config.unit ? ' ' + config.unit : ''}`;
}

function AssumptionCard({ paramKey, value, config, onChange }) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(value);

  const handleStartEdit = () => {
    if (config.type === 'select') return;
    setEditValue(config.type === 'percent' ? (value * 100) : value);
    setEditing(true);
  };

  const handleSave = () => {
    const newValue = config.type === 'percent' ? editValue / 100 : Number(editValue);
    onChange(paramKey, newValue);
    setEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSave();
    if (e.key === 'Escape') setEditing(false);
  };

  if (config.type === 'select') {
    return (
      <div className="bg-dark-800 border border-dark-700 rounded-lg p-3 hover:border-dark-500 transition-colors">
        <p className="text-xs text-gray-500 mb-1">{config.label}</p>
        <select
          value={value}
          onChange={(e) => onChange(paramKey, e.target.value)}
          className="bg-dark-700 border-none text-white text-sm rounded px-2 py-1 w-full focus:outline-none focus:ring-1 focus:ring-accent"
        >
          {config.options.map(opt => (
            <option key={opt} value={opt}>{config.display?.[opt] || opt}</option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div
      className="bg-dark-800 border border-dark-700 rounded-lg p-3 hover:border-accent/30 transition-colors cursor-pointer group"
      onClick={() => !editing && handleStartEdit()}
    >
      <p className="text-xs text-gray-500 mb-1">{config.label}</p>
      {editing ? (
        <div className="flex items-center gap-2">
          <input
            type="number"
            value={editValue}
            onChange={(e) => setEditValue(Number(e.target.value))}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            autoFocus
            step={config.type === 'percent' ? config.step * 100 : config.step}
            min={config.type === 'percent' ? (config.min || 0) * 100 : config.min}
            max={config.type === 'percent' ? (config.max || 100) * 100 : config.max}
            className="w-full bg-dark-700 border border-accent rounded px-2 py-1 text-white text-sm focus:outline-none"
          />
          <span className="text-xs text-gray-500">{config.type === 'percent' ? '%' : config.type === 'currency' ? 'CHF' : config.unit || ''}</span>
        </div>
      ) : (
        <p className="text-sm text-white font-medium group-hover:text-accent transition-colors">
          {formatValue(value, config)}
        </p>
      )}
    </div>
  );
}

export default function Assumptions({ parameters, onChange }) {
  const model = parameters.revenueModel || 'new_revenue';
  const relevantParams = MODEL_PARAMS[model] || MODEL_PARAMS.new_revenue;

  return (
    <div className="grid grid-cols-2 gap-3">
      {relevantParams.map((key) => {
        const config = PARAM_CONFIG[key];
        const value = parameters[key];
        if (config && value !== undefined) {
          return (
            <AssumptionCard
              key={key}
              paramKey={key}
              value={value}
              config={config}
              onChange={onChange}
            />
          );
        }
        return null;
      })}
    </div>
  );
}
