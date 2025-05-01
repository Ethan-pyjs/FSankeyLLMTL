import { useState, useRef } from 'react'
import SankeyChart from './SankeyChart'
import ReactMarkdown from 'react-markdown'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null) // Clear any previous errors
    }
  }

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
      setLoading(false)
      setError("Upload canceled by user")
    }
  }

  const handleUpload = async () => {
    // If no file is selected, open the file dialog
    if (!file) {
      fileInputRef.current?.click()
      return
    }
    
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError("Only PDF files are supported")
      return
    }
    
    setLoading(true)
    setError(null)

    // Create a new AbortController for this request
    abortControllerRef.current = new AbortController()
    const signal = abortControllerRef.current.signal

    const formData = new FormData()
    formData.append('file', file)
      
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/process`, {
        method: 'POST',
        body: formData,
        signal: signal
      })
      
      if (!res.ok) {
        throw new Error(`Server responded with status: ${res.status}`)
      }
      
      const data = await res.json()
      console.log("API Response:", data)
      
      // Validate income statement data
      if (data.income_statement && Object.keys(data.income_statement).length > 0) {
        setResponse(data)
      } else {
        throw new Error("No valid income statement data returned")
      }
      
    } catch (error) {
      // Don't show error message if the request was aborted
      if (error instanceof DOMException && error.name === 'AbortError') {
        console.log('Request aborted')
      } else {
        console.error("Error during upload:", error)
        setError(`Error processing file: ${error instanceof Error ? error.message : "Unknown error"}`)
      }
    } finally {
      setLoading(false)
      abortControllerRef.current = null
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
            
            <div className="flex gap-2">
              <button
                onClick={handleUpload}
                disabled={loading}
                className={`px-6 py-4 rounded-md font-medium transition-all duration-200 transform hover:scale-105 flex-1 ${
                  loading 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-purple-700 hover:bg-purple-600 text-white hover:shadow-lg'
                }`}
              >
                {loading ? 'Processing...' : file ? 'Upload and Analyze' : 'Select PDF and Analyze'}
              </button>
              
              {loading && (
                <button
                  onClick={handleCancel}
                  className="px-4 py-4 rounded-md font-medium transition-all duration-200 bg-red-700 hover:bg-red-600 text-white hover:shadow-lg hover:scale-105"
                >
                  Cancel
                </button>
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
              
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Financial Flow Visualization:</h2>
                <div className="sankey-container" style={{ minHeight: "250px" }}>
                  <SankeyChart incomeStatement={response.income_statement} />
                </div>
              </div>
              
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