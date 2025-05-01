export default function Changelog() {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-gray-900 bg-opacity-50 rounded-lg p-6 border border-purple-500 border-opacity-20">
          <h1 className="text-3xl font-bold text-purple-300 mb-4">Changelog</h1>
          <div className="space-y-4">
            <div className="border-b border-purple-500 border-opacity-20 pb-4">
              <h2 className="text-xl font-semibold text-purple-200">v1.0.0 ALPHA(2025-05-01)</h2>
              <ul className="list-disc list-inside text-gray-300 mt-2">
                <li>Initial release</li>
                <li>Added PDF parsing functionality</li>
                <li>Implemented Sankey diagram visualization</li>
                <li>Added AI-powered financial story generation</li>
              </ul>
            </div>
            <div className="border-b border-purple-500 border-opacity-20 pb-4">
              <h2 className="text-xl font-semibold text-purple-200">v1.1.0 ALPHA(2025-05-7)</h2>
              <ul className="list-disc list-inside text-gray-300 mt-2">
                <li>Improved Quality of Life</li>
                <li>Minor Fine Tuning</li>
                <li>Prepped for demonstration in class</li>
              </ul>
          </div>
        </div>
      </div>
    </div>
    );
  }