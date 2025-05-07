import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import SankeyChart from '../components/SankeyChart';
import BarChart from '../components/BarChart';
import WaterfallChart from '../components/WaterfallChart';
import FinancialStory from '../components/FinancialStory';
import GraphSelector from '../components/GraphSelector';
import PieChart from '../components/PieChart';
import MarginChart from '../components/MarginChart';

const Results = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [graphType, setGraphType] = useState('sankey');
  
  useEffect(() => {
    const { taskId } = location.state || {};
    if (!taskId) {
      navigate('/');
      return;
    }

    const eventSource = new EventSource(`http://127.0.0.1:8000/api/progress/${taskId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.status === 'completed') {
        setData({
          income_statement: data.income_statement,
          story: data.story
        });
        eventSource.close();
      } else if (data.status === 'error') {
        setError(data.error || 'An error occurred while processing');
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      setError('Lost connection to server');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [location.state, navigate]);

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-900 bg-opacity-30 text-red-200 p-4 rounded-md">
          {error}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      {/* Your visualization components */}
      <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-purple-200">Financial Visualizations</h2>
          <GraphSelector 
            selectedType={graphType} 
            onSelect={setGraphType} 
            options={[
              { value: 'sankey', label: 'Cash Flow Diagram' },
              { value: 'bar', label: 'Financial Metrics' },
              { value: 'waterfall', label: 'Profit Analysis' },
              { value: 'pie', label: 'Cost Distribution' },
              { value: 'margins', label: 'Margin Analysis' }
            ]}
          />
        </div>
        
        <div className="chart-container">
          <h3 className="text-xl font-semibold mb-4 text-purple-200">
            {graphType === 'sankey' && 'Cash Flow Visualization'}
            {graphType === 'bar' && 'Financial Metrics Overview'}
            {graphType === 'waterfall' && 'Profit Breakdown Analysis'}
            {graphType === 'pie' && 'Cost Distribution Analysis'}
            {graphType === 'margins' && 'Margin Performance Analysis'}
          </h3>
          
          {graphType === 'sankey' && (
            <SankeyChart incomeStatement={data.income_statement} />
          )}
          {graphType === 'bar' && (
            <BarChart incomeStatement={data.income_statement} />
          )}
          {graphType === 'waterfall' && (
            <WaterfallChart incomeStatement={data.income_statement} />
          )}
          {graphType === 'pie' && (
            <PieChart incomeStatement={data.income_statement} />
          )}
          {graphType === 'margins' && (
            <MarginChart incomeStatement={data.income_statement} />
          )}
        </div>
      </div>

      {/* Financial Story Section */}
      <div className="mt-8 bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
        <h2 className="text-xl font-semibold mb-4 text-purple-200">Financial Analysis</h2>
        <FinancialStory story={data.story} />
      </div>
    </div>
  );
};

export default Results;