import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface TrendChartProps {
  incomeStatement: {
    current_year?: {
      Revenue?: number;
      Cost_of_Revenue?: number;
      Gross_Profit?: number;
      Operating_Expenses?: number;
      Operating_Income?: number;
      Net_Income?: number;
    };
    previous_year?: {
      Revenue?: number;
      Cost_of_Revenue?: number;
      Gross_Profit?: number;
      Operating_Expenses?: number;
      Operating_Income?: number;
      Net_Income?: number;
    };
  };
}

export default function TrendChart({ incomeStatement }: TrendChartProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Transform data for comparison
  const metrics = ['Revenue', 'Gross_Profit', 'Operating_Income', 'Net_Income'];
  const data = metrics.map(metric => ({
    name: metric.replace('_', ' '),
    Current: incomeStatement.current_year?.[metric as keyof typeof incomeStatement.current_year] || 0,
    Previous: incomeStatement.previous_year?.[metric as keyof typeof incomeStatement.previous_year] || 0,
    Change: ((incomeStatement.current_year?.[metric as keyof typeof incomeStatement.current_year] || 0) /
      (incomeStatement.previous_year?.[metric as keyof typeof incomeStatement.previous_year] || 1) - 1) * 100
  }));

  return (
    <div className="space-y-4">
      <div style={{ width: '100%', height: '400px' }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 20, right: 30, left: 70, bottom: 60 }}>
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
              tickFormatter={formatCurrency}
              label={{ 
                value: 'Amount (USD)', 
                angle: -90, 
                position: 'insideLeft',
                style: { fill: '#999' }
              }}
            />
            <Tooltip
              formatter={(value: any) => formatCurrency(value)}
              contentStyle={{
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                border: '1px solid #8B5CF6',
                borderRadius: '4px',
                padding: '8px',
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="Current"
              stroke="#10B981"
              strokeWidth={2}
              dot={{ fill: '#10B981' }}
            />
            <Line
              type="monotone"
              dataKey="Previous"
              stroke="#8B5CF6"
              strokeWidth={2}
              dot={{ fill: '#8B5CF6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Year-over-Year Change Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-purple-500 border-opacity-20">
              <th className="py-2 px-4 text-purple-200">Metric</th>
              <th className="py-2 px-4 text-purple-200">Current Year</th>
              <th className="py-2 px-4 text-purple-200">Previous Year</th>
              <th className="py-2 px-4 text-purple-200">Change (%)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.name} className="border-b border-purple-500 border-opacity-10">
                <td className="py-2 px-4 text-gray-300">{row.name}</td>
                <td className="py-2 px-4 text-gray-200">{formatCurrency(row.Current)}</td>
                <td className="py-2 px-4 text-gray-200">{formatCurrency(row.Previous)}</td>
                <td className={`py-2 px-4 ${row.Change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {row.Change.toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}