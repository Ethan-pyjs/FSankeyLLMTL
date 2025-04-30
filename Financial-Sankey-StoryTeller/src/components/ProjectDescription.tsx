import { Github } from 'lucide-react';

export default function ProjectDescription() {
  return (
    <div className="w-full max-w-md mx-auto bg-black bg-opacity-40 p-6 md:p-8 rounded-lg shadow-xl border border-purple-500 border-opacity-20 backdrop-filter backdrop-blur-sm mb-6">
      <h2 className="text-xl font-semibold mb-4 text-purple-200">About This Project</h2>
      
      <div className="prose prose-sm text-gray-300 mb-6">
        <p className="mb-3">
          This is my school project, it plans to be a financial analysis tool that will do two things: Create a Sankey Chart and tell a story.
          This is done by uploading a PDF file containing the financial report of a company, 
          and the application will extract the income statement data from it. 
          The income statement will be extracted as a JSON and will be bucketed to fit for a graph. 
          This is all done with the power of LLMs (Large Language Models).
        </p>
        
        <p className="mb-3">
          What sets this apart from other financial analysis tools is the ability to visualize the flow of money through a Sankey chart, all in one click. Well...two if
          you're counting the upload.. But you get the point. The Sankey chart will show the flow of money from one category to another, 
          and the AI will generate a story based on the data.
        </p>
        
        <h3 className="text-lg font-medium text-purple-200 mt-4 mb-2">Features:</h3>
        <ul className="list-disc pl-5 space-y-1 mb-4">
          <li>PDF financial document parsing</li>
          <li>Interactive Sankey flow visualization</li>
          <li>AI-generated financial story and insights</li>
          <li>Clean, responsive interface</li>
        </ul>
        
        <p className="text-sm text-gray-400 italic">
        Built with React, TypeScript, Recharts, FastAPI, and powered by LLM technology. Remember AI is not perfect, so always verify the insights provided.
        </p>
      </div>
      
      <div className="flex justify-center">
        <a 
          href="https://github.com/Ethan-pyjs/FinancialProject" 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center px-4 py-2 bg-purple-700 hover:bg-purple-600 text-white rounded-md transition-all duration-200 transform hover:scale-105"
        >
          <Github size={18} className="mr-2" />
          View on GitHub
        </a>
      </div>
    </div>
  );
}