import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BarChartProps {
  incomeStatement: {
    Revenue?: number;
    Cost_of_Revenue?: number;
    Gross_Profit?: number;
    Operating_Expenses?: number;
    Operating_Income?: number;
    Net_Income?: number;
  };
}

export default function BarChart({ incomeStatement }: BarChartProps) {
  // Prepare data for the bar chart
  const data = Object.entries(incomeStatement)
    .filter(([key]) => key !== 'visualization_data') // Exclude visualization data
    .map(([key, value]) => ({
      name: key.replace(/_/g, ' '), // Replace underscores with spaces
      value: typeof value === 'number' ? value : 0,
    }));

  // Custom tooltip formatter
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
        <RechartsBarChart data={data} margin={{ top: 20, right: 30, left: 70, bottom: 60 }}>
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
            fill="#8B5CF6"
            radius={[4, 4, 0, 0]}
          />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}