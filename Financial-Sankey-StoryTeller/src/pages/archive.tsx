import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import NameAnalysisDialog from '../components/NameAnalysisDialog';

interface ArchiveItem {
  id: string;
  fileName: string;
  displayName: string;
  timestamp: string;
  results: any;
}

export default function Archive() {
  const [archives, setArchives] = useState<ArchiveItem[]>([]);
  const [isRenaming, setIsRenaming] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ArchiveItem | null>(null);

  useEffect(() => {
    const savedArchives = localStorage.getItem('financial-archives');
    if (savedArchives) {
      setArchives(JSON.parse(savedArchives));
    }
  }, []);

  const viewResults = (results: any) => {
    // Implement viewing logic here
    console.log('Viewing results:', results);
  };

  const deleteArchive = (id: string) => {
    const updatedArchives = archives.filter(item => item.id !== id);
    setArchives(updatedArchives);
    localStorage.setItem('financial-archives', JSON.stringify(updatedArchives));
  };

  const renameArchive = (id: string, newName: string) => {
    const updatedArchives = archives.map(item => 
      item.id === id ? { ...item, displayName: newName } : item
    );
    setArchives(updatedArchives);
    localStorage.setItem('financial-archives', JSON.stringify(updatedArchives));
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-gray-900 bg-opacity-50 rounded-lg p-6 border border-purple-500 border-opacity-20">
        <h1 className="text-3xl font-bold text-purple-300 mb-6">Analysis Archive (Not working yet)</h1>
        
        {archives.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No archived analyses yet.</p>
        ) : (
          <div className="grid gap-4">
            {archives.map((item) => (
              <div key={item.id} className="bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-purple-200">
                      {item.displayName || item.fileName}
                    </h3>
                    <p className="text-sm text-gray-400">
                      {format(new Date(item.timestamp), 'PPpp')}
                    </p>
                    <p className="text-xs text-gray-500">
                      File: {item.fileName}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedItem(item);
                        setIsRenaming(true);
                      }}
                      className="px-3 py-1 bg-gray-600 text-white rounded-md hover:bg-gray-500 transition-colors"
                    >
                      Rename
                    </button>
                    <button
                      onClick={() => viewResults(item.results)}
                      className="px-3 py-1 bg-purple-600 text-white rounded-md hover:bg-purple-500 transition-colors"
                    >
                      View
                    </button>
                    <button
                      onClick={() => deleteArchive(item.id)}
                      className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-500 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <NameAnalysisDialog
        isOpen={isRenaming}
        onClose={() => {
          setIsRenaming(false);
          setSelectedItem(null);
        }}
        onSave={(newName) => {
          if (selectedItem) {
            renameArchive(selectedItem.id, newName);
          }
        }}
        fileName={selectedItem?.displayName || selectedItem?.fileName || ''}
      />
    </div>
  );
}