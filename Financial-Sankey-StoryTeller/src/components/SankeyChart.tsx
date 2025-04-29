import { useState, useEffect } from 'react';
import { Sankey, Tooltip, Rectangle, ResponsiveContainer } from 'recharts';

interface SankeyNode {
  name: string;
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
    [key: string]: number | string | undefined;
  };
}

export default function SankeyChart({ incomeStatement }: SankeyChartProps) {
  const [data, setData] = useState<SankeyData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      if (!incomeStatement) return;
      
      console.log("Processing income statement data:", incomeStatement);
      
      // Clean and convert income statement data
      const cleanedData: Record<string, number> = {};
      const unknownFields: string[] = [];
      
      // Process each field and convert "Unknown" to estimated values
      Object.entries(incomeStatement).forEach(([key, value]) => {
        if (key === "error") return; // Skip error field
        
        // Convert string values to numbers if possible
        if (typeof value === "string") {
          if (value !== "Unknown") {
            const numValue = parseFloat(value);
            if (!isNaN(numValue)) {
              cleanedData[key] = numValue;
            } else {
              unknownFields.push(key);
            }
          } else {
            unknownFields.push(key);
          }
        } else if (typeof value === "number") {
          cleanedData[key] = value;
        } else {
          unknownFields.push(key);
        }
      });
      
      console.log("Cleaned data:", cleanedData);
      console.log("Unknown fields:", unknownFields);
      
      // If we have too many unknown values, we can't create a meaningful chart
      if (Object.keys(cleanedData).length < 2) {
        setError("Not enough financial data found to create a visualization");
        return;
      }
      
      // Estimate missing values if necessary
      if (!cleanedData.Revenue && cleanedData.Net_Income) {
        // Estimate Revenue based on typical net margin
        cleanedData.Revenue = Math.abs(cleanedData.Net_Income) / 0.15; // Assuming 15% net margin
      }
      
      if (cleanedData.Revenue) {
        // Ensure Revenue is positive for visualization purposes
        cleanedData.Revenue = Math.abs(cleanedData.Revenue);
        
        // Estimate Cost of Revenue if missing
        if (!cleanedData.Cost_of_Revenue) {
          cleanedData.Cost_of_Revenue = cleanedData.Revenue * 0.65; // Typical COGS ratio
        }
        
        // Estimate Gross Profit if missing
        if (!cleanedData.Gross_Profit) {
          cleanedData.Gross_Profit = cleanedData.Revenue - (cleanedData.Cost_of_Revenue || 0);
        }
        
        // Estimate Operating Expenses if missing
        if (!cleanedData.Operating_Expenses && cleanedData.Gross_Profit && cleanedData.Operating_Income) {
          cleanedData.Operating_Expenses = cleanedData.Gross_Profit - cleanedData.Operating_Income;
        } else if (!cleanedData.Operating_Expenses && cleanedData.Gross_Profit) {
          cleanedData.Operating_Expenses = cleanedData.Gross_Profit * 0.7; // Typical OpEx ratio
        }
        
        // Estimate Operating Income if missing
        if (!cleanedData.Operating_Income && cleanedData.Gross_Profit && cleanedData.Operating_Expenses) {
          cleanedData.Operating_Income = cleanedData.Gross_Profit - cleanedData.Operating_Expenses;
        }
        
        // Estimate Net Income if missing
        if (!cleanedData.Net_Income && cleanedData.Operating_Income) {
          cleanedData.Net_Income = cleanedData.Operating_Income * 0.75; // Accounting for taxes, etc.
        }
      }
      
      // Ensure all values are positive for visualization (absolute values)
      Object.keys(cleanedData).forEach(key => {
        cleanedData[key] = Math.abs(cleanedData[key] || 0);
      });
      
      // Create Sankey nodes
      const nodes: SankeyNode[] = [
        { name: 'Revenue' },
        { name: 'Cost of Revenue' },
        { name: 'Gross Profit' },
        { name: 'Operating Expenses' },
        { name: 'Operating Income' },
        { name: 'Taxes & Other' },
        { name: 'Net Income' }
      ];
      
      // Create Sankey links with appropriate values
      // Use a minimum value to ensure the flow is visible
      const minValue = Math.max(1, cleanedData.Revenue ? cleanedData.Revenue * 0.01 : 1);
      
      const links: SankeyLink[] = [
        // Revenue splits into Cost of Revenue and Gross Profit
        { 
          source: 0, 
          target: 1, 
          value: Math.max(minValue, cleanedData.Cost_of_Revenue || 0),
          absoluteValue: cleanedData.Cost_of_Revenue || 0
        },
        { 
          source: 0, 
          target: 2, 
          value: Math.max(minValue, cleanedData.Gross_Profit || 0),
          absoluteValue: cleanedData.Gross_Profit || 0
        },
        // Gross Profit splits into Operating Expenses and Operating Income
        { 
          source: 2, 
          target: 3, 
          value: Math.max(minValue, cleanedData.Operating_Expenses || 0),
          absoluteValue: cleanedData.Operating_Expenses || 0
        },
        { 
          source: 2, 
          target: 4, 
          value: Math.max(minValue, cleanedData.Operating_Income || 0),
          absoluteValue: cleanedData.Operating_Income || 0
        },
        // Operating Income splits into Taxes & Other and Net Income
        {
          source: 4,
          target: 5,
          value: Math.max(minValue, (cleanedData.Operating_Income || 0) - (cleanedData.Net_Income || 0)),
          absoluteValue: (cleanedData.Operating_Income || 0) - (cleanedData.Net_Income || 0)
        },
        { 
          source: 4, 
          target: 6, 
          value: Math.max(minValue, cleanedData.Net_Income || 0),
          absoluteValue: cleanedData.Net_Income || 0
        }
      ];
      
      setData({ nodes, links });
      setError(null);
      
      // Debug data
      console.log("Sankey Chart Data:", { nodes, links, cleanedData });
      
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

  return (
    <div className="w-full h-96">
      <div className="w-full h-full bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
        <ResponsiveContainer width="100%" height="100%">
          <Sankey
            data={data}
            node={
              <Rectangle 
                fill="#8B5CF6" 
                opacity={0.8}
              />
            }
            link={{ 
              stroke: "#4B5563",
              strokeOpacity: 0.5,
              fillOpacity: 0.5,
              fill: "#6D28D9"
            }}
            margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            nodePadding={30}
            nodeWidth={20}
          >
            <Tooltip 
              formatter={(value: any, name: any, props: any) => {
                // Use the absoluteValue if available for better display
                const displayValue = props.payload.absoluteValue !== undefined 
                  ? props.payload.absoluteValue 
                  : value;
                return formatCurrency(displayValue);
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
      <p className="text-xs text-gray-400 mt-2 italic">
        Note: Missing values are estimated based on standard financial ratios. For accurate visualization, ensure all income statement values are properly extracted.
      </p>
    </div>
  );
}