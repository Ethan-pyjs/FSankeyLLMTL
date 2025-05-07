import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MarginChartProps {
  incomeStatement: {
    Revenue?: number;
    Gross_Profit?: number;
    Operating_Income?: number;
    Net_Income?: number;
  };
}

export default function MarginChart({ incomeStatement }: MarginChartProps) {
  const calculateMargins = () => {
    const revenue = incomeStatement.Revenue || 1;
    return [
      {
        name: 'Gross Margin',
        value: ((incomeStatement.Gross_Profit || 0) / revenue) * 100
      },
      {
        name: 'Operating Margin',
        value: ((incomeStatement.Operating_Income || 0) / revenue) * 100
      },
      {
        name: 'Net Margin',
        value: ((incomeStatement.Net_Income || 0) / revenue) * 100
      }
    ];
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      <ResponsiveContainer>
        <BarChart data={calculateMargins()}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value: number | string) => {
            if (typeof value === 'number') {
              return `${value.toFixed(2)}%`;
            }
            return value;
          }} />
          <Bar dataKey="value" fill="#8B5CF6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}