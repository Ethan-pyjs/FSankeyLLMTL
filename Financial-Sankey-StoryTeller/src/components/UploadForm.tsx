import { useState, useRef, useEffect } from 'react'
import SankeyChart from './SankeyChart'
import ReactMarkdown from 'react-markdown'
import GraphSelector from './GraphSelector'
import BarChart from './BarChart';
import WaterfallChart from './WaterfallChart';

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [graphType, setGraphType] = useState('sankey');
  const [shouldSaveToArchive, setShouldSaveToArchive] = useState(true);
  const [contextNotes, setContextNotes] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (taskId) {
      const eventSource = new EventSource(`http://127.0.0.1:8000/api/progress/${taskId}`);
      let retryCount = 0;
      const maxRetries = 3;

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("Progress update:", data);

          if (data.status === "error") {
            console.error("Server reported error:", data.error);
            setError(data.error || "An error occurred during processing");
            setLoading(false);
            eventSource.close();
            return;
          }

          // Update progress
          setProgress(data.progress || 0);
          setProgressMessage(data.message || "Processing...");

          // Handle completion
          if (data.status === "completed") {
            console.log("Processing completed:", data);
            const results = {
              income_statement: data.income_statement,
              story: data.story,
              processing_time: data.processing_time
            };
            setResponse(results);
            
            // Only save if checkbox is checked
            if (shouldSaveToArchive && file) {
              saveToArchive(results, file.name, file.name);
            }
            
            setLoading(false);
            eventSource.close();
          }
        } catch (error) {
          console.error("Error parsing SSE data:", error);
          retryCount++;
          if (retryCount >= maxRetries) {
            setError("Failed to process updates from server");
            setLoading(false);
            eventSource.close();
          }
        }
      };

      eventSource.onerror = (error) => {
        console.error("EventSource error:", error);
        retryCount++;
        if (retryCount >= maxRetries) {
          setError("Lost connection to server. Please try again.");
          setLoading(false);
          eventSource.close();
        }
      };

      return () => {
        eventSource.close();
      };
    }
  }, [taskId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      
      // Validate file type
      if (!selectedFile.name.toLowerCase().endsWith('.pdf') || selectedFile.type !== 'application/pdf') {
        setError("Only PDF files are supported")
        // Reset file input
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
        return
      }
      
      setFile(selectedFile)
      setError(null) // Clear any previous errors
    }
  }

  const handleUpload = async () => {
    if (!file) {
      fileInputRef.current?.click()
      return
    }
    
    setLoading(true)
    setError(null)
    setProgress(0)
    setProgressMessage('Starting upload...')

    const formData = new FormData()
    formData.append('file', file)
      
    try {
      // First get the task ID
      const res = await fetch(`http://127.0.0.1:8000/api/process`, {
        method: 'POST',
        body: formData,
      })
      
      if (!res.ok) {
        throw new Error(`Server responded with status: ${res.status}`)
      }
      
      const { task_id } = await res.json()
      setTaskId(task_id)
      
    } catch (error) {
      console.error("Error during upload:", error)
      setError(`Error processing file: ${error instanceof Error ? error.message : "Unknown error"}`)
      setLoading(false)
    }
  }

  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      // Format numbers as currency
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value);
    }
    return String(value);
  };

  const saveToArchive = (results: any, fileName: string, displayName: string) => {
    const archiveItem = {
      id: crypto.randomUUID(),
      fileName,
      displayName,
      timestamp: new Date().toISOString(),
      contextNotes: contextNotes.trim() || null, // Include context notes
      results
    };

    const savedArchives = localStorage.getItem('financial-archives');
    const archives = savedArchives ? JSON.parse(savedArchives) : [];
    archives.unshift(archiveItem);
    localStorage.setItem('financial-archives', JSON.stringify(archives));
    cleanupOldArchives();
  };

  // Add this utility function
  const cleanupOldArchives = () => {
    const savedArchives = localStorage.getItem('financial-archives');
    if (savedArchives) {
      const archives = JSON.parse(savedArchives);
      // Keep only last 20 entries
      const trimmedArchives = archives.slice(0, 20);
      localStorage.setItem('financial-archives', JSON.stringify(trimmedArchives));
    }
  };

  return (
    <div className="flex flex-col items-center w-full">
      <div className="w-full max-w-md mx-auto bg-black bg-opacity-40 p-6 md:p-8 rounded-lg shadow-xl border border-purple-500 border-opacity-20 backdrop-filter backdrop-blur-sm">
        <div className="mb-6">
          <input
            type="file"
            ref={fileInputRef}
            accept="application/pdf,.pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          
          <div className="flex flex-col">
            {file && (
              <>
                <div className="mb-4 p-3 bg-gray-800 bg-opacity-50 rounded-md border border-purple-500 border-opacity-30">
                  <span className="text-gray-300 flex items-center justify-between">
                    <span className="font-medium">Selected file:</span>
                    <span className="ml-2 truncate">{file.name}</span>
                  </span>
                </div>
                
                <div className="w-full space-y-4">
                  <div className="space-y-3">
                    <label className="block text-gray-300 text-sm font-medium">
                      Add Context Notes (optional)
                    </label>
                    <textarea
                      value={contextNotes}
                      onChange={(e) => setContextNotes(e.target.value)}
                      placeholder="Add any additional context or notes about this financial document..."
                      className="w-full h-24 px-3 py-2 text-gray-300 bg-gray-800 bg-opacity-50 
                        rounded-md border border-purple-500 border-opacity-30 
                        focus:border-purple-400 focus:ring-1 focus:ring-purple-400 
                        focus:outline-none resize-none"
                    />
                  </div>

                  <label className="flex items-center space-x-2 mb-4 text-gray-300">
                    <input
                      type="checkbox"
                      checked={shouldSaveToArchive}
                      onChange={(e) => setShouldSaveToArchive(e.target.checked)}
                      className="form-checkbox h-4 w-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                    />
                    <span>Save analysis to archive</span>
                  </label>
                </div>
              </>
            )}
            
            <div className="flex items-center space-x-4">
              <button
                onClick={handleUpload}
                disabled={loading}
                className={`px-6 py-4 rounded-md font-medium transition-all duration-200 transform hover:scale-105 ${
                  loading 
                    ? 'bg-gray-600 cursor-not-allowed w-48' 
                    : 'bg-purple-700 hover:bg-purple-600 text-white hover:shadow-lg w-48'
                }`}
              >
                {loading ? 'Processing...' : file ? 'Upload and Analyze' : 'Select PDF'}
              </button>

              {loading && (
                <div className="flex-1">
                  <div className="bg-gray-700 bg-opacity-50 rounded-full h-4 overflow-hidden">
                    <div 
                      className="bg-purple-600 h-full transition-all duration-500 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-1">
                    <p className="text-sm text-gray-300">{progressMessage}</p>
                    <p className="text-xs text-gray-400">{progress}% complete</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-900 bg-opacity-30 text-red-200 rounded-md border border-red-500 border-opacity-30">
              {error}
            </div>
          )}
        </div>

        {response && (
          <div className="mt-8">
            <div className="grid grid-cols-1 gap-6">
              {/* Income Statement Data Table */}
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Income Statement Data:</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-purple-500 border-opacity-20">
                        <th className="py-2 px-4 text-purple-200 font-semibold">Metric</th>
                        <th className="py-2 px-4 text-purple-200 font-semibold">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(response.income_statement)
                        .filter(([key]) => !key.includes('visualization_data')) // Exclude visualization data
                        .map(([key, value]) => (
                          <tr 
                            key={key} 
                            className="border-b border-purple-500 border-opacity-10 hover:bg-purple-900 hover:bg-opacity-20 transition-colors"
                          >
                            <td className="py-2 px-4 text-gray-300">
                              {key.replace(/_/g, ' ')}
                            </td>
                            <td className="py-2 px-4 text-gray-200 font-mono">
                              {formatValue(value)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {/* Financial Visualization Section */}
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
                  {graphType === 'sankey' && (
                    <SankeyChart incomeStatement={response.income_statement} />
                  )}
                  {graphType === 'bar' && (
                    <BarChart incomeStatement={response.income_statement} />
                  )}
                  {graphType === 'waterfall' && (
                    <WaterfallChart incomeStatement={response.income_statement} />
                  )}
                  {graphType === 'year-over-year' && (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-gray-400">Year-over-Year analysis coming soon...</p>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Financial Analysis Section */}
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Financial Analysis:</h2>
                <div className="bg-blue-800 p-4 rounded overflow-y-auto max-h-80 text-gray-200 text-left">
                  <ReactMarkdown>
                    {response.story}
                  </ReactMarkdown>
                </div>
                <p className="text-xs text-gray-400 mt-2 italic text-right">
                  Processing time: {response.processing_time || "N/A"}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}