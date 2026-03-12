import { useMemo } from 'react';
import {
  ComposedChart, Bar, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Legend,
} from 'recharts';

function formatCHF(value) {
  if (Math.abs(value) >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(0)}K`;
  return value.toFixed(0);
}

function SummaryCard({ label, value, unit, highlight, delay = 0 }) {
  return (
    <div
      className="bg-dark-800 border border-dark-700 rounded-xl p-4 slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-2xl font-bold ${highlight ? 'text-accent' : 'text-white'}`}>
        {value}
      </p>
      {unit && <p className="text-xs text-gray-500 mt-0.5">{unit}</p>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-dark-800 border border-dark-700 rounded-lg p-3 shadow-xl">
      <p className="text-xs text-gray-400 mb-2">Month {label}</p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-gray-400">{entry.name}:</span>
          <span className="text-white font-medium">CHF {formatCHF(entry.value)}</span>
        </div>
      ))}
    </div>
  );
};

export default function Dashboard({ projection, parameters }) {
  const chartData = useMemo(() => {
    if (!projection) return [];
    return projection.months.map((m, i) => ({
      month: m,
      impact: projection.impact[i],
      costs: -projection.totalCosts[i],
      net: projection.net[i],
      cumulative: projection.cumulative[i],
    }));
  }, [projection]);

  if (!projection) return null;

  const { breakEvenMonth, totalInvestment, annualImpact, monthlyRunCost, runwayMonth } = projection;

  return (
    <div className="space-y-6 fade-in">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <SummaryCard
          label="Total Investment"
          value={`CHF ${formatCHF(totalInvestment)}`}
          delay={0}
        />
        <SummaryCard
          label="Monthly Run Cost"
          value={`CHF ${formatCHF(monthlyRunCost)}`}
          unit="per month"
          delay={100}
        />
        <SummaryCard
          label="Annual Impact"
          value={`CHF ${formatCHF(annualImpact)}`}
          unit="first 12 months"
          delay={200}
        />
        <SummaryCard
          label="Break-even"
          value={breakEvenMonth ? `Month ${Math.ceil(breakEvenMonth)}` : '>24 months'}
          highlight={!!breakEvenMonth}
          delay={300}
        />
      </div>

      {/* Main Chart */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-6 slide-up" style={{ animationDelay: '400ms' }}>
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
          24-Month Financial Projection
        </h3>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
            <XAxis
              dataKey="month"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={{ stroke: '#1a1a2e' }}
              tickLine={false}
              label={{ value: 'Month', position: 'insideBottom', offset: -5, fill: '#6b7280', fontSize: 11 }}
            />
            <YAxis
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={{ stroke: '#1a1a2e' }}
              tickLine={false}
              tickFormatter={(v) => formatCHF(v)}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11, color: '#9ca3af' }}
            />
            <ReferenceLine y={0} stroke="#374151" strokeWidth={1} />
            {breakEvenMonth && breakEvenMonth <= 24 && (
              <ReferenceLine
                x={Math.ceil(breakEvenMonth)}
                stroke="#14b8a6"
                strokeDasharray="5 5"
                strokeWidth={2}
                label={{
                  value: 'Break-even',
                  position: 'top',
                  fill: '#14b8a6',
                  fontSize: 11,
                }}
              />
            )}
            <Bar
              dataKey="costs"
              name="Costs"
              fill="#ef4444"
              fillOpacity={0.7}
              radius={[0, 0, 2, 2]}
            />
            <Area
              type="monotone"
              dataKey="impact"
              name="Revenue Impact"
              stroke="#14b8a6"
              fill="#14b8a6"
              fillOpacity={0.15}
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="cumulative"
              name="Cumulative Net"
              stroke="#818cf8"
              fill="none"
              strokeWidth={2}
              strokeDasharray="5 5"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Runway indicator */}
      {runwayMonth && (
        <div className="bg-red-900/20 border border-red-800/30 rounded-xl p-4 slide-up" style={{ animationDelay: '500ms' }}>
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span className="text-red-300 text-sm font-medium">
              Budget depleted at month {runwayMonth} (CHF {formatCHF(projection.startingBudget)} starting budget)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
