import { useState, useEffect } from 'react';
import { Sankey, Tooltip, Rectangle, ResponsiveContainer } from 'recharts';

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
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      if (!incomeStatement) return;
      
      // Convert entire income statement object to a single string for analysis
      const allText = JSON.stringify(incomeStatement);
      
      // Function to find all monetary values in text
      const findMonetaryValues = (text: string) => {
        // Match patterns like "$33.9 billion" or "33.9 billion dollars" or "$33,916"
        const regex = /\$?(\d+(?:[.,]\d+)?)\s*(?:billion|million|thousand|[mb]|k)?/gi;
        const matches = [...text.matchAll(regex)];
        
        return matches.map(match => {
          const value = parseFloat(match[1].replace(/,/g, ''));
          const unit = match[0].toLowerCase();
          
          if (unit.includes('billion') || unit.includes('b')) {
            return value * 1000000000;
          } else if (unit.includes('million') || unit.includes('m')) {
            return value * 1000000;
          } else if (unit.includes('thousand') || unit.includes('k')) {
            return value * 1000;
          }
          return value;
        });
      };
      
      // Find all monetary values in the text
      const values = findMonetaryValues(allText);
      
      // Sort values in descending order
      const sortedValues = [...values].sort((a, b) => b - a);
      
      // If we have fewer than 2 values, we can't create a meaningful chart
      if (sortedValues.length < 2) {
        setError("Not enough financial data found to create a visualization");
        return;
      }
      
      // Use the largest value as revenue
      const estimatedRevenue = sortedValues[0];
      
      // Find net income - try to find it in the text or use a medium-sized value
      let netIncome = 0;
      
      // Look for net income in the text
      if (allText.toLowerCase().includes('net income')) {
        const netIncomeIndex = allText.toLowerCase().indexOf('net income');
        const netIncomeText = allText.substring(netIncomeIndex, netIncomeIndex + 200);
        const netIncomeValues = findMonetaryValues(netIncomeText);
        
        if (netIncomeValues.length > 0) {
          netIncome = netIncomeValues[0];
        }
      }
      
      // If we couldn't find net income, use a mid-sized value from our sorted list
      if (netIncome === 0 && sortedValues.length > 2) {
        netIncome = sortedValues[Math.floor(sortedValues.length / 2)];
      }
      
      // Calculate other financials based on typical ratios
      const estimatedCostOfRevenue = estimatedRevenue * 0.65;
      const estimatedGrossProfit = estimatedRevenue - estimatedCostOfRevenue;
      const estimatedOpEx = estimatedGrossProfit - netIncome;
      
      // Create Sankey nodes and links
      const nodes = [
        { name: 'Revenue' },
        { name: 'Cost of Revenue' },
        { name: 'Gross Profit' },
        { name: 'Operating Expenses' },
        { name: 'Net Income' }
      ];
      
      // Ensure all values are positive and significant
      const safeValue = (val: number) => Math.max(estimatedRevenue * 0.001, Math.abs(val));
      
      const links = [
        { source: 0, target: 1, value: safeValue(estimatedCostOfRevenue) },
        { source: 0, target: 2, value: safeValue(estimatedGrossProfit) },
        { source: 2, target: 3, value: safeValue(estimatedOpEx) },
        { source: 2, target: 4, value: safeValue(netIncome) }
      ];
      
      setData({ nodes, links });
      setError(null);
    } catch (err) {
      console.error("Error creating Sankey chart:", err);
      setError("Failed to create visualization. Please check console for details.");
    }
  }, [incomeStatement]);
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(2)} billion`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)} million`;
    } else {
      return `$${value.toLocaleString()}`;
    }
  };

  if (error) {
    return (
      <div className="w-full mt-6 p-4 bg-red-50 border border-red-200 rounded">
        <h2 className="text-xl font-semibold mb-2">Income Flow Visualization</h2>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="w-full mt-6 p-4 bg-gray-50 border border-gray-200 rounded">
        <h2 className="text-xl font-semibold mb-2">Income Flow Visualization</h2>
        <p>Loading chart data...</p>
      </div>
    );
  }

  return (
    <div className="w-full h-96 mt-6">
      <h2 className="text-xl font-semibold mb-4">Income Flow Visualization</h2>
      <div className="w-full h-full bg-white rounded shadow p-4">
        <ResponsiveContainer width="100%" height="100%">
          <Sankey
            data={data}
            node={<Rectangle fill="#34d399" opacity={0.8} />}
            link={{ stroke: "#aaa" }}
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            nodePadding={50}
            nodeWidth={10}
          >
            <Tooltip 
              formatter={(value: number) => formatCurrency(value)}
              labelFormatter={(name) => `${name}`}
            />
          </Sankey>
        </ResponsiveContainer>
      </div>
      <p className="text-sm text-gray-500 mt-2">
        Note: The chart generation function is still a work in progress...
      </p>
    </div>
  );
}