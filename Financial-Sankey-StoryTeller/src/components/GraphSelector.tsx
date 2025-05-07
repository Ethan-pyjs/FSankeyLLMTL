import type { FC } from 'react';

interface GraphOption {
  value: string;
  label: string;
}

interface GraphSelectorProps {
  selectedType: string;
  onSelect: (type: string) => void;
  options: GraphOption[];
}

const GraphSelector: FC<GraphSelectorProps> = ({ selectedType, onSelect, options }) => {
  return (
    <div className="flex gap-2">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onSelect(option.value)}
          className={`px-3 py-1 rounded-md text-sm transition-colors ${
            selectedType === option.value
              ? 'bg-purple-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default GraphSelector;