import { ComposedChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface WaterfallChartProps {
  incomeStatement: {
    Revenue?: number;
    Cost_of_Revenue?: number;
    Gross_Profit?: number;
    Operating_Expenses?: number;
    Operating_Income?: number;
    Net_Income?: number;
  };
}

export default function WaterfallChart({ incomeStatement }: WaterfallChartProps) {
  // Transform data for waterfall chart
  const data = [
    { name: 'Revenue', value: incomeStatement.Revenue || 0 },
    { name: 'Cost of Revenue', value: -(incomeStatement.Cost_of_Revenue || 0) },
    { name: 'Gross Profit', value: incomeStatement.Gross_Profit || 0 },
    { name: 'Operating Expenses', value: -(incomeStatement.Operating_Expenses || 0) },
    { name: 'Operating Income', value: incomeStatement.Operating_Income || 0 },
    { name: 'Net Income', value: incomeStatement.Net_Income || 0 },
  ];

  const formatTooltip = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer>
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 70, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={80}
            stroke="#999"
          />
          <YAxis
            stroke="#999"
            tickFormatter={(value) => formatTooltip(value)}
          />
          <Tooltip
            formatter={(value: any) => formatTooltip(value)}
            contentStyle={{
              backgroundColor: 'rgba(17, 24, 39, 0.95)',
              border: '1px solid #8B5CF6',
              borderRadius: '4px',
              padding: '8px',
            }}
          />
          <Bar
            dataKey="value"
            fill="#10B981"
            stroke="#0E9F6E"
            strokeWidth={1}
            radius={[4, 4, 0, 0]}
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.value > 0 ? '#10B981' : '#EF4444'}
                stroke={entry.value > 0 ? '#0E9F6E' : '#DC2626'}
              />
            ))}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}