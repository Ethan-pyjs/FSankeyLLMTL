import UploadForm from './components/UploadForm'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-center mb-6">10-K Analyzer</h1>
      <UploadForm />
    </div>
  )
}