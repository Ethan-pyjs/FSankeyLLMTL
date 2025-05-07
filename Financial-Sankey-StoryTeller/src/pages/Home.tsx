// src/pages/Home.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      
      // Validate file type and size
      if (!file.name.toLowerCase().endsWith('.pdf') || file.type !== 'application/pdf') {
        setError("Only PDF files are supported");
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        setError("File size must be less than 10MB");
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedFile) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // First get the task ID
      const response = await fetch('http://127.0.0.1:8000/api/process', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.task_id) {
        // Redirect to the results page with the task ID
        navigate('/results', { 
          state: { 
            taskId: data.task_id,
            fileName: selectedFile.name 
          } 
        });
      } else {
        throw new Error('No task ID received from server');
      }
      
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error instanceof Error ? error.message : 'An error occurred while uploading the file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-10">Financial Sankey Story-Teller</h1>
      
      <div className="w-full max-w-6xl bg-gray-900 bg-opacity-70 p-8 rounded-lg shadow-xl border border-purple-800 border-opacity-30">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="flex flex-col items-center justify-center p-6 border border-dashed border-purple-500 border-opacity-40 rounded-lg">
            <form onSubmit={handleSubmit} className="w-full">
              <div className="mb-6 text-center">
                <svg className="mx-auto h-12 w-12 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                <h2 className="mt-2 text-xl font-medium text-white">Upload Financial Document</h2>
                <p className="mt-1 text-sm text-gray-300">PDF files only (Max. 10MB)</p>
              </div>
              <div className="mt-4">
                <label htmlFor="file-upload" className="w-full cursor-pointer bg-purple-800 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md inline-flex items-center justify-center transition-colors">
                  <span>Browse Files</span>
                  <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} accept=".pdf" />
                </label>
              </div>
              {selectedFile && (
                <div className="mt-4 text-left">
                  <p className="text-sm text-gray-300">Selected file:</p>
                  <div className="flex items-center mt-1 bg-gray-800 bg-opacity-70 p-2 rounded">
                    <svg className="h-5 w-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                    </svg>
                    <span className="ml-2 text-sm text-gray-300 truncate">{selectedFile.name}</span>
                    <span className="ml-auto text-xs text-gray-400">{Math.round(selectedFile.size / 1024)} KB</span>
                  </div>
                </div>
              )}
              {error && (
                <div className="mt-4 p-3 bg-red-900 bg-opacity-30 text-red-200 rounded-md border border-red-500 border-opacity-30">
                  {error}
                </div>
              )}
              <button 
                type="submit" 
                className={`mt-6 w-full py-2 px-4 bg-gradient-to-r from-purple-700 to-purple-600 text-white font-medium rounded-md 
                  ${!loading && 'hover:from-purple-600 hover:to-purple-500 hover:scale-105'}
                  focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50 
                  transition-all transform 
                  disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none`}
                disabled={!selectedFile || loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </div>
                ) : (
                  'Analyze Document'
                )}
              </button>
            </form>
          </div>
          
          {/* Preview/Information Section */}
          <div className="flex flex-col h-full">
            <div className="bg-gray-800 bg-opacity-50 p-6 rounded-lg flex-grow">
              <h3 className="text-lg font-medium text-white mb-4">How It Works</h3>
              <ol className="space-y-4 text-left text-gray-300">
                <li className="flex">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-800 flex items-center justify-center mr-3 text-xs">1</span>
                  <span>Upload your financial document (PDF)</span>
                </li>
                <li className="flex">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-800 flex items-center justify-center mr-3 text-xs">2</span>
                  <span>LLM AI reads and analyzes the financial data</span>
                </li>
                <li className="flex">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-800 flex items-center justify-center mr-3 text-xs">3</span>
                  <span>Get a human-readable story about your finances</span>
                </li>
                <li className="flex">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-purple-800 flex items-center justify-center mr-3 text-xs">4</span>
                  <span>View interactive Sankey charts to visualize money flow</span>
                </li>
              </ol>
              
              <div className="mt-6 p-4 bg-purple-900 bg-opacity-30 rounded border border-purple-700 border-opacity-30">
                <p className="text-sm text-gray-300">
                  <span className="font-semibold text-purple-300">Note:</span> This is a school project, results from this tool should not be used for real financial decisions.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;