import { useState } from 'react'

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [response, setResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)

    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch('http://localhost:8000/api/process', {
      method: 'POST',
      body: formData,
    })

    const data = await res.json()
    setResponse(data)
    setLoading(false)
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
