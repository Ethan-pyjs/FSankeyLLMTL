import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface PieChartProps {
  incomeStatement: {
    Revenue?: number;
    Cost_of_Revenue?: number;
    Operating_Expenses?: number;
  };
}

export default function PieChart({ incomeStatement }: PieChartProps) {
  const data = [
    { name: 'Cost of Revenue', value: incomeStatement.Cost_of_Revenue || 0 },
    { name: 'Operating Expenses', value: incomeStatement.Operating_Expenses || 0 }
  ];

  const COLORS = ['#8B5CF6', '#6D28D9'];

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
        <RechartsPieChart>
          <Pie
            data={data}
            innerRadius={60}
            outerRadius={120}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={formatTooltip} />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  );
}