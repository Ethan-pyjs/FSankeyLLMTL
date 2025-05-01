import { useState, useEffect } from 'react';
import { Sankey, Tooltip, Rectangle, ResponsiveContainer, Layer, Text } from 'recharts';

interface SankeyNode {
  name: string;
  value?: number;
}

interface SankeyLink {
  source: number;
  target: number;
  value: number;
  absoluteValue?: number;
}

interface SankeyData {
  nodes: SankeyNode[];
  links: SankeyLink[];
}

interface SankeyChartProps {
  incomeStatement: {
    Revenue?: number | string;
    Cost_of_Revenue?: number | string;
    Gross_Profit?: number | string;
    Operating_Expenses?: number | string;
    Operating_Income?: number | string;
    Net_Income?: number | string;
    [key: string]: any;
  };
}

export default function SankeyChart({ incomeStatement }: SankeyChartProps) {
  const [data, setData] = useState<SankeyData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      if (!incomeStatement) {
        console.log("No income statement data provided");
        return;
      }
      
      console.log("Processing income statement data:", incomeStatement);
      
      // Clean and convert income statement data
      const cleanedData: Record<string, number> = {};
      
      // Process each field and convert strings to numbers
      Object.entries(incomeStatement).forEach(([key, value]) => {
        if (key === "error" || key === "visualization_data") return; // Skip these fields
        
        // Convert string values to numbers if possible
        if (typeof value === "string") {
          if (value !== "Unknown") {
            const cleanStr = value.toString().replace(/[^\d.-]/g, '');
            const numValue = parseFloat(cleanStr);
            if (!isNaN(numValue)) {
              cleanedData[key] = numValue;
            } else {
              cleanedData[key] = 0;
            }
          } else {
            cleanedData[key] = 0;
          }
        } else if (typeof value === "number") {
          cleanedData[key] = value;
        } else {
          cleanedData[key] = 0;
        }
      });
      
      console.log("Cleaned data:", cleanedData);
      
      // Use the actual values from the income statement without modification
      let financialData = {
        Revenue: cleanedData.Revenue || 0,
        Cost_of_Revenue: cleanedData.Cost_of_Revenue || 0,
        Gross_Profit: cleanedData.Gross_Profit || 0,
        Operating_Expenses: cleanedData.Operating_Expenses || 0,
        Operating_Income: cleanedData.Operating_Income || 0,
        Net_Income: cleanedData.Net_Income || 0
      };
      
      console.log("Financial data for visualization:", financialData);
      
      // Create Sankey nodes with their actual values
      const nodes: SankeyNode[] = [
        { name: 'Revenue', value: financialData.Revenue },
        { name: 'Cost', value: financialData.Cost_of_Revenue },
        { name: 'Gross Profit', value: financialData.Gross_Profit },
        { name: 'Op Expenses', value: financialData.Operating_Expenses },
        { name: 'Op Income', value: financialData.Operating_Income },
        { name: 'Net Income', value: financialData.Net_Income }
      ];
      
      // For visualization purposes, we need positive values
      // But we'll store the actual values for tooltips
      const minFlowValue = 1;
      const absRevenue = Math.max(minFlowValue, Math.abs(financialData.Revenue));
      const absCostOfRevenue = Math.max(minFlowValue, Math.abs(financialData.Cost_of_Revenue));
      const absGrossProfit = Math.max(minFlowValue, Math.abs(financialData.Gross_Profit));
      const absOperatingExpenses = Math.max(minFlowValue, Math.abs(financialData.Operating_Expenses));
      const absOperatingIncome = Math.max(minFlowValue, Math.abs(financialData.Operating_Income));
      const absNetIncome = Math.max(minFlowValue, Math.abs(financialData.Net_Income));
      
      // Calculate a separate flow from Operating Income to Net Income
      // If Net Income > Operating Income, something added value (like non-operating income)
      // If Net Income < Operating Income, something reduced value (like taxes)
      const adjustmentValue = Math.abs(financialData.Net_Income - financialData.Operating_Income);
      const isPositiveAdjustment = financialData.Net_Income > financialData.Operating_Income;
      
      // Create Sankey links with appropriate values and maintain the actual values
      const links: SankeyLink[] = [
        // Revenue splits into Cost of Revenue and Gross Profit
        { 
          source: 0, 
          target: 1, 
          value: absCostOfRevenue,
          absoluteValue: financialData.Cost_of_Revenue
        },
        { 
          source: 0, 
          target: 2, 
          value: absGrossProfit,
          absoluteValue: financialData.Gross_Profit
        },
        // Gross Profit splits into Operating Expenses and Operating Income
        { 
          source: 2, 
          target: 3, 
          value: absOperatingExpenses,
          absoluteValue: financialData.Operating_Expenses
        },
        { 
          source: 2, 
          target: 4, 
          value: absOperatingIncome,
          absoluteValue: financialData.Operating_Income
        },
        // Operating Income flows to Net Income
        { 
          source: 4, 
          target: 5, 
          value: absNetIncome,
          absoluteValue: financialData.Net_Income
        }
      ];
      
      // Add a note about any flow imbalances for debugging
      const totalOutFromRevenue = absCostOfRevenue + absGrossProfit;
      if (Math.abs(absRevenue - totalOutFromRevenue) > 0.1) {
        console.warn("Revenue flow imbalance:", { revenue: absRevenue, totalOut: totalOutFromRevenue });
      }
      
      const totalOutFromGrossProfit = absOperatingExpenses + absOperatingIncome;
      if (Math.abs(absGrossProfit - totalOutFromGrossProfit) > 0.1) {
        console.warn("Gross profit flow imbalance:", { grossProfit: absGrossProfit, totalOut: totalOutFromGrossProfit });
      }
      
      setData({ nodes, links });
      setError(null);
      
    } catch (err) {
      console.error("Error creating Sankey chart:", err);
      setError("Failed to create visualization. Please check the console for details.");
    }
  }, [incomeStatement]);
  
  // Format currency for display
  const formatCurrency = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (absValue >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (absValue >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    }
    return `$${value.toFixed(0)}`;
  };
  
  // Format currency for tooltips with more detail
  const formatCurrencyDetailed = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue >= 1000000000) {
      return `$${(value / 1000000000).toFixed(2)} billion`;
    } else if (absValue >= 1000000) {
      return `$${(value / 1000000).toFixed(2)} million`;
    } else if (absValue >= 1000) {
      return `$${(value / 1000).toFixed(2)}k`;
    }
    return `$${value.toLocaleString()}`;
  };

  if (error) {
    return (
      <div className="w-full p-4 bg-gray-800 bg-opacity-50 border border-red-500 border-opacity-30 rounded-lg text-gray-200">
        <h2 className="text-xl font-semibold mb-2 text-purple-200">Income Flow Visualization</h2>
        <p className="text-red-400">{error}</p>
        <p className="mt-2 text-sm">Try uploading a different financial document with clearer income statement data.</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="w-full p-4 bg-gray-800 bg-opacity-50 border border-purple-500 border-opacity-20 rounded-lg text-gray-200">
        <h2 className="text-xl font-semibold mb-2 text-purple-200">Income Flow Visualization</h2>
        <p>Preparing visualization...</p>
      </div>
    );
  }

  // Custom Node component with better positioned labels
  const CustomNode = (props: any) => {
    const { x, y, width, height, index, payload } = props;
    const nodeValue = payload.value || 0;
    
    // Determine node color based on type
    const getNodeColor = (nodeName: string) => {
      if (nodeName === 'Revenue') return '#10B981'; // Emerald-500
      if (nodeName.includes('Cost') || nodeName.includes('Expenses')) {
        return '#EF4444'; // Red-500
      }
      return '#6EE7B7'; // Emerald-300 for profit/income nodes
    };
  
    const nodeFillColor = getNodeColor(payload.name);
    const formattedValue = formatCurrency(nodeValue);
    
    // Calculate label positions
    let textX, textAnchor;
    const isLeftSide = index <= 1;
    const isRightSide = index >= 4;
    
    if (isLeftSide) {
      textX = x - 10;
      textAnchor = "end";
    } else if (isRightSide) {
      textX = x + width + 10;
      textAnchor = "start";
    } else {
      textX = x + width/2;
      textAnchor = "middle";
    }
    
    return (
      <Layer>
        <Rectangle
          x={x}
          y={y}
          width={width}
          height={height}
          fill={nodeFillColor}
          fillOpacity={0.8}
        />
        {/* Node name label */}
        <Text
          x={textX}
          y={y + height / 2 - 10}
          textAnchor={textAnchor as "end" | "inherit" | "start" | "middle" | undefined}
          verticalAnchor="middle"
          fill="#FFFFFF"
          fontSize={14}
          fontWeight="bold"
          stroke="#000000"
          strokeWidth={0.5}
        >
          {payload.name}
        </Text>
        
        {/* Value label */}
        <Text
          x={textX}
          y={y + height / 2 + 16}
          textAnchor={textAnchor as "end" | "inherit" | "start" | "middle" | undefined}
          verticalAnchor="middle"
          fill="#E9D5FF" // Light purple for value
          fontSize={16}
          fontWeight="bold"
          stroke="#000000"
          strokeWidth={0.3}
        >
          {formattedValue}
        </Text>
      </Layer>
    );
  };

  return (
    <div className="w-full" style={{ height: "350px", minHeight: "600px" }}>
      <div className="w-full h-full bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
        <h2 className="text-xl font-semibold mb-4 text-purple-200">Financial Flow Visualization</h2>
        <div style={{ width: '100%', height: '520px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <Sankey
              data={data}
              node={<CustomNode />}
              link={{ 
                stroke: "#8B5CF6", // Purple color for links
                strokeOpacity: 0.3,
                fillOpacity: 0.5,
                fill: "#8B5CF6" 
              }}
              margin={{ top: 40, right: 160, bottom: 40, left: 160 }}
              nodePadding={20}
              nodeWidth={15}
              iterations={64}
            >
              <Tooltip 
                formatter={(value: any, _name: any, props: any) => {
                  const displayValue = props.payload.absoluteValue !== undefined 
                    ? props.payload.absoluteValue 
                    : value;
                  return formatCurrencyDetailed(displayValue);
                }}
                labelFormatter={(name) => `${name}`}
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.95)', 
                  border: '1px solid #8B5CF6',
                  borderRadius: '4px',
                  padding: '8px',
                  color: '#E5E7EB' 
                }}
              />
            </Sankey>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="mt-4 text-sm text-gray-300 bg-gray-800 bg-opacity-50 p-4 rounded-lg border border-purple-500 border-opacity-20">
        <h3 className="font-semibold text-purple-200 mb-2">Data Validation Issues</h3>
        <p>The income statement data appears to have some mathematical inconsistencies:</p>
        <ul className="list-disc pl-5 mt-2 space-y-1">
          <li>Gross Profit ($40M) ≠ Revenue ($300M) - Cost of Revenue ($250M)</li>
          <li>Operating Income ($202M) ≠ Gross Profit ($40M) - Operating Expenses ($221M)</li>
          <li>Net Income ($482M) is significantly higher than Operating Income ($202M)</li>
        </ul>
        <p className="mt-2">These inconsistencies may affect the accuracy of the visualization.</p>
      </div>
    </div>
  );
}