import { useState } from 'react'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  // In UploadForm.tsx, modify the handleUpload function
const handleUpload = async () => {
  if (!file) return
  setLoading(true)

  const formData = new FormData()
  formData.append('file', file)

  try {
    console.log("Sending request to backend...")
    const res = await fetch('http://127.0.0.1:8000/api/process', {
      method: 'POST',
      body: formData,
    })
    
    console.log("Received response:", res)
    
    if (!res.ok) {
      throw new Error(`Server responded with status: ${res.status}`)
    }
    
    const data = await res.json()
    console.log("Parsed data:", data)
    
    setResponse(data)
  } catch (error) {
    console.error("Error during upload:", error)
    // Optionally show an error message to the user
    alert("Error processing file. Check console for details.")
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow">
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

      {response && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Income Statement:</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
            {JSON.stringify(response.income_statement, null, 2)}
          </pre>

          <h2 className="text-xl font-semibold mt-4 mb-2">Generated Story:</h2>
          <p className="bg-gray-50 p-4 rounded">{response.story}</p>
        </div>
      )}
    </div>
  )
}
