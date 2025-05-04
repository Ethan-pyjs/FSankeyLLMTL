import type { FC } from 'react';

interface GraphSelectorProps {
  onSelect: (type: string) => void;
  currentType: string;
}

const GraphSelector: FC<GraphSelectorProps> = ({ onSelect, currentType }) => {
  const graphTypes = [
    { id: 'sankey', name: 'Sankey Flow' },
    { id: 'bar', name: 'Bar Chart' },
    { id: 'waterfall', name: 'Waterfall' },
    { id: 'trend', name: 'Year Comparison' },
    { id: 'all', name: 'All Graphs' }
  ];

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {graphTypes.map((type) => (
        <button
          key={type.id}
          onClick={() => onSelect(type.id)}
          className={`px-4 py-2 rounded-md transition-all ${
            currentType === type.id
              ? 'bg-purple-600 text-white'
              : 'bg-gray-800 text-gray-300 hover:bg-purple-700'
          }`}
        >
          {type.name}
        </button>
      ))}
    </div>
  );
};

export default GraphSelector;