import { useState } from 'react'
import SankeyChart from './SankeyChart'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)

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
      console.log("Parsed data:", data)
      
      setResponse(data)
    } catch (error) {
      console.error("Error during upload:", error)
      alert("Error processing file. Check console for details.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto bg-white p-6 rounded-xl shadow">
      <div className="mb-6">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-4"
        />
        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Upload and Analyze'}
        </button>
      </div>

      {response && (
        <div className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-2">Income Statement:</h2>
              <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto max-h-80">
                {JSON.stringify(response.income_statement, null, 2)}
              </pre>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-2">Generated Story:</h2>
              <p className="bg-gray-50 p-4 rounded overflow-y-auto max-h-80">
                {response.story}
              </p>
            </div>
          </div>
          
          {/* Add the Sankey chart */}
          <SankeyChart incomeStatement={response.income_statement} />
        </div>
      )}
    </div>
  )
}
