import { Github } from 'lucide-react';

export default function ProjectDescription() {
  return (
    <div className="w-full max-w-md mx-auto bg-black bg-opacity-40 p-6 md:p-8 rounded-lg shadow-xl border border-purple-500 border-opacity-20 backdrop-filter backdrop-blur-sm mb-6">
      <h2 className="text-xl font-semibold mb-4 text-purple-200">About This Project</h2>
      
      <div className="prose prose-sm text-gray-300 mb-6">
        <p className="mb-3">
          This project plans to do many things in one click. All you have to do is upload a PDF financial document, and the AI will parse the document,
          analyze the data, and generate a story about the data. The AI will also generate a Sankey chart that shows the flow of money from one category to another.
        </p>
        
        <p className="mb-3">
          Its meant as a tool for anyone who wants to understand their financial data better. Whether you're a business owner, a student, or just someone who wants to get a better grasp of their finances,
          this tool can help you visualize and understand your data in a way that is easy to digest. The AI-generated story will help you understand the data in a more human-readable format, and the Sankey chart will help you see the flow of money in a more visual way.
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