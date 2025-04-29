import { useState, useRef } from 'react'
import SankeyChart from './SankeyChart'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null) // Clear any previous errors
    }
  }

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a PDF file first")
      return
    }
    
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError("Only PDF files are supported")
      return
    }
    
    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/api/process`, {
        method: 'POST',
        body: formData,
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
      console.error("Error during upload:", error)
      setError(`Error processing file: ${error instanceof Error ? error.message : "Unknown error"}`)
    } finally {
      setLoading(false)
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
          
          <div className="flex flex-col gap-4">
            <button 
              onClick={handleButtonClick}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white py-3 px-4 rounded-md flex items-center justify-between border border-purple-500 border-opacity-30 transition-all duration-200"
            >
              <span className="mr-2 font-medium">Browse </span>
              <span className="text-gray-300 text-sm truncate max-w-xs">
                {file ? file.name : 'Select a PDF file'}
              </span>
            </button>
            
            <button
              onClick={handleUpload}
              disabled={loading || !file}
              className={`px-6 py-3 rounded-md font-medium transition-all duration-200 transform hover:scale-105 w-full ${
                loading || !file 
                  ? 'bg-gray-600 cursor-not-allowed' 
                  : 'bg-purple-700 hover:bg-purple-600 text-white hover:shadow-lg'
              }`}
            >
              {loading ? 'Processing...' : 'Upload and Analyze'}
            </button>
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
                <SankeyChart incomeStatement={response.income_statement} />
              </div>
              
              <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 border border-purple-500 border-opacity-20">
                <h2 className="text-xl font-semibold mb-2 text-purple-200">Financial Analysis:</h2>
                <div className="bg-black bg-opacity-30 p-4 rounded overflow-y-auto max-h-80 text-gray-200 text-left">
                  {response.story}
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