import { useState, useEffect } from 'react';
import { format } from 'date-fns';

interface ArchiveItem {
  id: string;
  fileName: string;
  timestamp: string;
  results: any;
}

export default function Archive() {
  const [archives, setArchives] = useState<ArchiveItem[]>([]);

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

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-gray-900 bg-opacity-50 rounded-lg p-6 border border-purple-500 border-opacity-20">
        <h1 className="text-3xl font-bold text-purple-300 mb-6">Analysis Archive</h1>
        
        {archives.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No archived analyses yet.</p>
        ) : (
          <div className="grid gap-4">
            {archives.map((item) => (
              <div key={item.id} className="bg-gray-800 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-purple-200">{item.fileName}</h3>
                    <p className="text-sm text-gray-400">
                      {format(new Date(item.timestamp), 'PPpp')}
                    </p>
                  </div>
                  <div className="flex gap-2">
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
    </div>
  );
}