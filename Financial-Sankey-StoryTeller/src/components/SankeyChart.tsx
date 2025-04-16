import { useState, useEffect } from 'react';
import { Sankey, Tooltip, Rectangle} from 'recharts';

interface SankeyNode {
  name: string;
}

interface SankeyLink {
  source: number;
  target: number;
  value: number;
}

interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

interface SankeyChartProps {
  incomeStatement: any;
}

export default function SankeyChart({ incomeStatement }: SankeyChartProps) {
  const [data, setData] = useState<SankeyData | null>(null);

  useEffect(() => {
    if (!incomeStatement) return;

    // Extract numerical values from income statement
    const extractValue = (val: string | number): number => {
      if (typeof val === 'number') return val;
      const numMatch = val.match(/[\d,\.]+/);
      return numMatch ? parseFloat(numMatch[0].replace(/,/g, '')) : 0;
    };

    // Create nodes array
    const nodes = [
      { name: 'Revenue' },
      { name: 'Cost of Revenue' },
      { name: 'Gross Profit' },
      { name: 'Operating Expenses' },
      { name: 'Net Income' }
    ];

    // Create links for the Sankey diagram
    let links = [];
    
    const revenue = extractValue(incomeStatement.Revenue || '0');
    const costOfRevenue = extractValue(incomeStatement['Cost of Revenue'] || '0');
    const grossProfit = extractValue(incomeStatement['Gross Profit'] || '0');
    const opEx = extractValue(incomeStatement['Operating Expenses'] || '0');
    const netIncome = extractValue(incomeStatement['Net Income'] || '0');

    // If values are missing, calculate them
    const calculatedGrossProfit = revenue - costOfRevenue;
    const calculatedNetIncome = grossProfit - opEx;

    links = [
      { source: 0, target: 1, value: costOfRevenue || (revenue * 0.6) },  // Revenue to Cost of Revenue
      { source: 0, target: 2, value: grossProfit || calculatedGrossProfit },  // Revenue to Gross Profit
      { source: 2, target: 3, value: opEx || (grossProfit * 0.7) },  // Gross Profit to Operating Expenses
      { source: 2, target: 4, value: netIncome || calculatedNetIncome }  // Gross Profit to Net Income
    ];

    setData({ nodes, links });
  }, [incomeStatement]);

  if (!data) return <div>Loading chart data...</div>;

  return (
    <div className="w-full h-64 mt-6">
      <h2 className="text-xl font-semibold mb-4">Income Flow Visualization</h2>
      <div className="w-full h-full bg-white rounded shadow">
        <Sankey
          width={600}
          height={400}
          data={data}
          node={<Rectangle fill="#34d399" opacity={0.8} />}
          link={{ stroke: "#aaa" }}
          margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
        >
          <Tooltip />
        </Sankey>
      </div>
    </div>
  );
}