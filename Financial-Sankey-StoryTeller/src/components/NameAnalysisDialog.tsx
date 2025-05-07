// Create new file: src/components/NameAnalysisDialog.tsx
import { useState } from 'react';

interface NameAnalysisDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string) => void;
  fileName: string;
}

export default function NameAnalysisDialog({ isOpen, onClose, onSave, fileName }: NameAnalysisDialogProps) {
  const [name, setName] = useState(fileName);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-lg p-6 max-w-md w-full border border-purple-500 border-opacity-20">
        <h2 className="text-xl font-semibold text-purple-200 mb-4">Name Your Analysis</h2>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full bg-gray-800 text-white px-3 py-2 rounded-md border border-purple-500 border-opacity-20 focus:border-purple-400 focus:outline-none"
          placeholder="Enter a name for this analysis"
        />
        <div className="flex justify-end gap-3 mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-300 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onSave(name);
              onClose();
            }}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-500 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}