export default function About() {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-6 border border-purple-500 border-opacity-20">
          <h1 className="text-3xl font-bold text-purple-300 mb-4">About Me</h1>
          <div className="prose prose-invert">
            <p className="text-gray-300">
              {/* Add your about me content here */}
              I am a passionate developer interested in financial technology and data visualization...
            </p>
          </div>
        </div>
      </div>
    );
  }