import { useState, useRef } from 'react'
import SankeyChart from './SankeyChart'
import FinancialStory from './FinancialStory'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [processingProgress, setProcessingProgress] = useState<number>(0);
  const [processingPhase, setProcessingPhase] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null) // Clear any previous errors
    }
  }

  const handleUpload = async () => {
    if (!file) {
      fileInputRef.current?.click();
      return;
    }
    
    setLoading(true);
    setError(null);
    setUploadProgress(0);
    setProcessingProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // First upload the file
      const uploadResponse = await fetch('http://127.0.0.1:8000/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.statusText}`);
      }

      const data = await uploadResponse.json();
      
      // Start listening for processing progress
      const eventSource = new EventSource(`http://127.0.0.1:8000/api/progress/${data.task_id}`);
      
      eventSource.onmessage = (event) => {
        const progressData = JSON.parse(event.data);
        setProcessingProgress(progressData.progress);
        setProcessingPhase(progressData.phase);
      };

      eventSource.onerror = () => {
        eventSource.close();
        setProcessingProgress(100);
      };

      // Update your state with the response data
      if (data.income_statement && Object.keys(data.income_statement).length > 0) {
        setResponse(data);
      } else {
        throw new Error("No valid income statement data returned");
      }

    } catch (error) {
      console.error("Error during processing:", error);
      setError(`Error processing file: ${error instanceof Error ? error.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center w-full">
      <div className="w-full max-w-md mx-auto bg-black bg-opacity-40 p-6 md:p-8 rounded-lg shadow-xl border border-purple-500 border-opacity-20 backdrop-filter backdrop-blur-sm">
        <div className="mb-6">
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          
          <div className="flex flex-col">
            {file && (
              <div className="mb-4 p-3 bg-gray-800 bg-opacity-50 rounded-md border border-purple-500 border-opacity-30">
                <span className="text-gray-300 flex items-center justify-between">
                  <span className="font-medium">Selected file:</span>
                  <span className="ml-2 truncate">{file.name}</span>
                </span>
              </div>
            )}
            
            <button
              onClick={handleUpload}
              disabled={loading}
              className={`px-6 py-4 rounded-md font-medium transition-all duration-200 transform hover:scale-105 w-full ${
                loading 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-purple-700 hover:bg-purple-600 text-white hover:shadow-lg'
              }`}
            >
              {loading ? 'Processing...' : file ? 'Upload and Analyze' : 'Select PDF and Analyze'}
            </button>

            {/* Progress bar with improved styling and animation */}
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="mt-4">
                <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-purple-600 h-full rounded-full transition-all duration-300 ease-in-out"
                    style={{ 
                      width: `${uploadProgress}%`,
                      transition: 'width 0.3s ease-in-out'
                    }}
                  />
                </div>
                <div className="text-xs text-gray-400 text-center mt-1">
                  Uploading: {Math.round(uploadProgress)}%
                </div>
              </div>
            )}

            {/* Processing progress bar */}
            {processingProgress > 0 && (
              <div className="mt-4">
                <div className="w-full bg-gray-700 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-purple-600 h-full rounded-full transition-all duration-300 ease-in-out"
                    style={{ 
                      width: `${processingProgress}%`,
                      transition: 'width 0.3s ease-in-out'
                    }}
                  />
                </div>
                <div className="text-xs text-gray-400 text-center mt-1">
                  {processingPhase}: {Math.round(processingProgress)}%
                </div>
              </div>
            )}
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
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Income Statement Data:</h2>
                <pre className="bg-black bg-opacity-50 p-4 rounded text-sm overflow-x-auto max-h-60 text-gray-200">
                  {JSON.stringify(response.income_statement, null, 2)}
                </pre>
              </div>
              
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Financial Flow Visualization:</h2>
                <div className="sankey-container" style={{ minHeight: "250px" }}>
                  <SankeyChart incomeStatement={response.income_statement} />
                </div>
              </div>
              
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Financial Analysis:</h2>
                <div className="bg-black bg-opacity-30 p-4 rounded overflow-y-auto max-h-80 text-gray-200 text-left">
                  <FinancialStory story={response.story} />
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