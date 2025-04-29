import UploadForm from './components/UploadForm'

export default function App() {
  return (
    <div className="flex min-h-screen w-full bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Left sidebar */}
      <div className="hidden md:block w-1/6 bg-black bg-opacity-30 p-6">
        <div className="h-full border-r border-purple-800 border-opacity-30"></div>
      </div>
      
      {/* Main content */}
      <div className="flex flex-col items-center justify-center flex-1 p-4 md:p-8">
        <div className="w-full max-w-md">
          <h1 className="text-4xl font-bold mb-8 text-center text-white">10-K Analyzer</h1>
          <UploadForm />
        </div>
      </div>
      
      {/* Right sidebar */}
      <div className="hidden md:block w-1/6 bg-black bg-opacity-30 p-6">
        <div className="h-full border-l border-purple-800 border-opacity-30"></div>
      </div>
    </div>
  )
}