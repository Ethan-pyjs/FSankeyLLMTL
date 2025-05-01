import { useState, useEffect } from 'react';
import { Sankey, Tooltip, Rectangle, ResponsiveContainer, Layer, Text } from 'recharts';

interface SankeyNode {
  name: string;
  value?: number; // Add value property to store the node's value
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
      if (!incomeStatement) {
        console.log("No income statement data provided");
        return;
      }
      
      console.log("Processing income statement data:", incomeStatement);
      
      // Clean and convert income statement data
      const cleanedData: Record<string, number> = {};
      const unknownFields: string[] = [];
      
      // Process each field and convert strings to numbers
      Object.entries(incomeStatement).forEach(([key, value]) => {
        if (key === "error") return; // Skip error field
        
        // Debug the type and value
        console.log(`Processing field ${key}: ${value} (${typeof value})`);
        
        // Convert string values to numbers if possible
        if (typeof value === "string") {
          if (value !== "Unknown") {
            // Remove commas and any non-numeric characters except decimal point and negative sign
            const cleanStr = value.toString().replace(/[^\d.-]/g, '');
            const numValue = parseFloat(cleanStr);
            console.log(`Converting string '${value}' to number: ${numValue}`);
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
      
      // Check if we have valid data for the main financial metrics
      const hasInvalidValues = Object.values(cleanedData).some(value => value === 0 || isNaN(value));
      const hasSufficientData = Object.keys(cleanedData).length >= 2;
      
      if (!hasSufficientData || hasInvalidValues) {
        console.warn("Data validation failed:", { hasSufficientData, hasInvalidValues, cleanedData });
      }
      
      // Create consistent financial data structure, filling in missing values
      let financialData = {
        Revenue: cleanedData.Revenue || 0,
        Cost_of_Revenue: cleanedData.Cost_of_Revenue || 0,
        Gross_Profit: cleanedData.Gross_Profit || 0,
        Operating_Expenses: cleanedData.Operating_Expenses || 0,
        Operating_Income: cleanedData.Operating_Income || 0,
        Net_Income: cleanedData.Net_Income || 0
      };
      
      // Handle case where Revenue exists but Cost_of_Revenue and Gross_Profit don't align
      if (financialData.Revenue > 0) {
        // If gross profit is missing, calculate it
        if (financialData.Gross_Profit === 0) {
          if (financialData.Cost_of_Revenue > 0) {
            financialData.Gross_Profit = financialData.Revenue - financialData.Cost_of_Revenue;
          } else {
            // Estimate Cost of Revenue if missing
            financialData.Cost_of_Revenue = financialData.Revenue * 0.65; // Typical COGS ratio
            financialData.Gross_Profit = financialData.Revenue - financialData.Cost_of_Revenue;
          }
        } 
        // If cost of revenue is missing but we have gross profit
        else if (financialData.Cost_of_Revenue === 0) {
          financialData.Cost_of_Revenue = financialData.Revenue - financialData.Gross_Profit;
        }
      }
      
      // Handle operating income calculation
      if (financialData.Gross_Profit > 0) {
        // If operating income is missing, calculate it
        if (financialData.Operating_Income === 0) {
          if (financialData.Operating_Expenses > 0) {
            financialData.Operating_Income = financialData.Gross_Profit - financialData.Operating_Expenses;
          } else {
            // Estimate Operating Expenses if missing
            financialData.Operating_Expenses = financialData.Gross_Profit * 0.7; // Typical OpEx ratio
            financialData.Operating_Income = financialData.Gross_Profit - financialData.Operating_Expenses;
          }
        } 
        // If operating expenses is missing but we have operating income
        else if (financialData.Operating_Expenses === 0) {
          financialData.Operating_Expenses = financialData.Gross_Profit - financialData.Operating_Income;
        }
      }
      
      // Handle net income calculation
      if (financialData.Operating_Income !== 0 && financialData.Net_Income === 0) {
        // Estimate Net Income if missing
        financialData.Net_Income = financialData.Operating_Income * 0.75; // Accounting for taxes, etc.
      }
      
      // If some key metrics are still missing, try to infer from available data
      if (financialData.Revenue === 0 && financialData.Gross_Profit > 0) {
        financialData.Revenue = financialData.Gross_Profit * 1.5; // Estimate revenue from gross profit
        financialData.Cost_of_Revenue = financialData.Revenue - financialData.Gross_Profit;
      }
      
      // Handle case where Net Income exists but other values are missing
      if (financialData.Net_Income !== 0 && financialData.Operating_Income === 0) {
        financialData.Operating_Income = financialData.Net_Income * 1.25; // Reverse estimate
      }
      
      // Calculate tax and other expenses (removed unused variable)
      
      console.log("Processed financial data:", financialData);
      
      // Create default nodes for known metrics
      const nodes: SankeyNode[] = [
        { name: 'Revenue', value: financialData.Revenue },
        { name: 'Cost', value: financialData.Cost_of_Revenue },
        { name: 'Gross Profit', value: financialData.Gross_Profit },
        { name: 'Op Expenses', value: financialData.Operating_Expenses },
        { name: 'Op Income', value: financialData.Operating_Income },
        { name: 'Net Income', value: financialData.Net_Income }
      ];
      
      // Ensure all values are positive for visualization (use absolute values)
      // and ensure minimum values for visibility
      const minFlowValue = 1;
      const revenue = Math.max(minFlowValue, Math.abs(financialData.Revenue));
      const costOfRevenue = Math.max(minFlowValue, Math.abs(financialData.Cost_of_Revenue));
      const grossProfit = Math.max(minFlowValue, Math.abs(financialData.Gross_Profit));
      const operatingExpenses = Math.max(minFlowValue, Math.abs(financialData.Operating_Expenses));
      const operatingIncome = Math.max(minFlowValue, Math.abs(financialData.Operating_Income));
      const netIncome = Math.max(minFlowValue, Math.abs(financialData.Net_Income));
      
      // Create links for known flows (unchanged)
      const links: SankeyLink[] = [
        { 
          source: 0, 
          target: 1, 
          value: costOfRevenue,
          absoluteValue: financialData.Cost_of_Revenue
        },
        { 
          source: 0, 
          target: 2, 
          value: grossProfit,
          absoluteValue: financialData.Gross_Profit
        },
        { 
          source: 2, 
          target: 3, 
          value: operatingExpenses,
          absoluteValue: financialData.Operating_Expenses
        },
        { 
          source: 2, 
          target: 4, 
          value: operatingIncome,
          absoluteValue: financialData.Operating_Income
        },
        { 
          source: 4, 
          target: 5, 
          value: netIncome,
          absoluteValue: financialData.Net_Income
        }
      ];
      
      // --- New Code for Handling Extra Buckets ---
      // Define the known keys matching your financialData keys
      const knownKeys = ["Revenue", "Cost_of_Revenue", "Gross_Profit", "Operating_Expenses", "Operating_Income", "Net_Income"];

      // Sum up any extra values returned in the incomeStatement
      let extraSum = 0;
      Object.entries(incomeStatement).forEach(([key, value]) => {
        if (!knownKeys.includes(key)) {
          const num = Number(value);
          if (!isNaN(num)) {
            extraSum += Math.abs(num);
          }
        }
      });

      // If extra buckets exist, add an "Other" node and corresponding link
      if (extraSum > 0) {
        const otherNodeIndex = nodes.length;
        nodes.push({ name: 'Other', value: extraSum });
        
        // For example, add a link from Revenue (index 0) to Other
        links.push({
          source: 0,
          target: otherNodeIndex,
          value: extraSum,
          absoluteValue: extraSum
        });
      }

      // Add a validation step to ensure the sum of incoming values roughly equals the sum of outgoing values
      // This makes the Sankey diagram look more natural
      
      // Check revenue -> (cost of revenue + gross profit)
      const totalOutFromRevenue = costOfRevenue + grossProfit;
      if (Math.abs(revenue - totalOutFromRevenue) > 0.1) {
        console.warn("Revenue flow mismatch:", { revenue, totalOutFromRevenue });
      }
      
      // Check gross profit -> (operating expenses + operating income)
      const totalOutFromGrossProfit = operatingExpenses + operatingIncome;
      if (Math.abs(grossProfit - totalOutFromGrossProfit) > 0.1) {
        console.warn("Gross profit flow mismatch:", { grossProfit, totalOutFromGrossProfit });
      }
      
      // Check operating income -> (taxes & other + net income)
      const totalOutFromOperatingIncome = netIncome;
      if (Math.abs(operatingIncome - totalOutFromOperatingIncome) > 0.1) {
        console.warn("Operating income flow mismatch:", { operatingIncome, totalOutFromOperatingIncome });
      }
      
      setData({ nodes, links });
      setError(null);
      
    } catch (err) {
      console.error("Error creating Sankey chart:", err);
      setError("Failed to create visualization. Please check the console for details.");
    }
  }, [incomeStatement]);
  
  // Format currency values for display
  const formatCurrency = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(1)}B`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(1)}K`;
    } else {
      return `$${value.toFixed(0)}`;
    }
  };
  
  // Format currency for tooltip (more detailed)
  const formatCurrencyDetailed = (value: number) => {
    if (value >= 1000000000) {
      return `$${(value / 1000000000).toFixed(2)} billion`;
    } else if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(2)} million`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(2)}k`;
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

  // Add debug information
  console.log("Sankey data being rendered:", data);
  
  // Enhanced custom Node component with dollar value labels
  const CustomNode = (props: any) => {
    const { x, y, width, height, index, payload } = props;
    
    // Get the node's value from the payload or default to 0
    const nodeValue = payload.value || 0;
    
    // Format the value for display
    const formattedValue = formatCurrency(nodeValue);
    
    // Determine label position based on node position in the flow
    const isLeftNode = index === 0; // Revenue
    const isRightNode = index === 5; // Net Income
    const isCenterLeftNode = index === 2; // Gross Profit
    const isCenterRightNode = index === 4; // Operating Income
    
    // Position text based on node location in flow
    let textX, textAnchor;
    
    if (isLeftNode) {
      textX = x + width + 5;
      textAnchor = "start";
    } else if (isRightNode) {
      textX = x - 5;
      textAnchor = "end";
    } else if (isCenterLeftNode) {
      textX = x - 5;
      textAnchor = "end";
    } else if (isCenterRightNode) {
      textX = x + width + 5;
      textAnchor = "start";
    } else {
      // For other nodes, place text on top of the node
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
          fill="#8B5CF6"
          fillOpacity={0.8}
        />
        {/* Node name label */}
        <Text
          x={textX}
          y={isCenterLeftNode || isCenterRightNode ? y + height / 2 - 10 : y - 10}
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
        
        {/* Value label - positioned below the name */}
        <Text
          x={textX}
          y={isCenterLeftNode || isCenterRightNode ? y + height / 2 + 10 : y + 10}
          textAnchor={textAnchor as "end" | "inherit" | "start" | "middle" | undefined}
          verticalAnchor="middle"
          fill="#E9D5FF" // Light purple for the value
          fontSize={17}
          fontWeight="bold"
          fontStyle="italic"
          stroke="#000000"
          strokeWidth={0.3}
        >
          {formattedValue}
        </Text>
      </Layer>
    );
  };

  return (
    <div className="w-full" style={{ height: "350px", minHeight: "300px" }}> {/* Increased height to accommodate labels */}
      <div className="w-full h-full bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
        {/* Force a specific height for the container to ensure visibility */}
        <div style={{ width: '100%', height: '300px', position: 'relative' }}> {/* Increased height */}
          <ResponsiveContainer width="100%" height="100%">
            <Sankey
              data={data}
              node={<CustomNode />}
              link={{ 
                stroke: "#4B5563",
                strokeOpacity: 0.6,
                fillOpacity: 0.5,
                fill: "#6D28D9"
              }}
              // Improved margins to keep everything in view with the added labels
              margin={{ top: 20, right: 100, bottom: 5, left: 50 }}
              nodePadding={5} // Increased padding between nodes for value labels
              nodeWidth={13}
              iterations={64}
            >
              <Tooltip 
                formatter={(value: any, _name: any, props: any) => {
                  // Use the absoluteValue if available for better display
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
      <p className="text-xs text-gray-400 mt-2 italic">
        Note: Missing values are estimated based on standard financial ratios. For accurate visualization, ensure all income statement values are properly extracted.
      </p>
    </div>
  );
}