import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface FinancialStoryProps {
  story: string;
}

export default function FinancialStory({ story }: FinancialStoryProps) {
  const [markdownStory, setMarkdownStory] = useState<string>('');
  
  useEffect(() => {
    if (!story) return;
    
    // Convert the story to markdown format
    const formattedMarkdown = convertToMarkdown(story);
    setMarkdownStory(formattedMarkdown);
  }, [story]);
  
  const convertToMarkdown = (storyText: string): string => {
    // If there are already paragraph breaks, we'll enhance those
    if (storyText.includes('\n\n')) {
      let paragraphs = storyText.split('\n\n');
      
      // Process each paragraph and check if it's a potential header
      return paragraphs.map((paragraph) => {
        // Check if paragraph looks like a header (short, ends with colon, or all caps)
        if (paragraph.length < 50 && (paragraph.endsWith(':') || paragraph.toUpperCase() === paragraph)) {
          // Convert to markdown header and remove trailing colon
          return `\n## ${paragraph.replace(/:\s*$/, '')}\n`;
        } 
        
        // Format regular paragraphs with number highlighting
        return formatParagraphWithHighlights(paragraph);
      }).join('\n\n');
    } else {
      // If there are no paragraph breaks, try to split by sentences and identify sections
      const sentences = storyText.match(/[^.!?]+[.!?]+/g) || [];
      
      // Define patterns for section identification
      const keywordPatterns = [
        { pattern: /overview|summary|analysis/i, title: "Overview" },
        { pattern: /revenue|sales|income/i, title: "Revenue Analysis" },
        { pattern: /profit margin|gross profit|margin/i, title: "Profit Margin Analysis" },
        { pattern: /expenses|costs|expenditure/i, title: "Expense Analysis" },
        { pattern: /net income|bottom line|earnings/i, title: "Net Income" },
        { pattern: /recommend|suggest|advice|future/i, title: "Recommendations" },
        { pattern: /trend|growth|decline|increase|decrease/i, title: "Trends" },
        { pattern: /compare|comparison|versus|vs\.|benchmark/i, title: "Comparisons" },
        { pattern: /ratio|financial health|liquidity/i, title: "Financial Health" }
      ];
      
      // Find section title for a sentence
      const findSectionTitle = (sentence: string) => {
        for (const { pattern, title } of keywordPatterns) {
          if (pattern.test(sentence)) {
            return title;
          }
        }
        return null;
      };
      
      // Group sentences into markdown sections
      let markdownSections: string[] = [];
      let currentTitle = "Overview"; // Default title
      let currentSection: string[] = [];
      
      sentences.forEach((sentence, index) => {
        // Check if this sentence should start a new section
        const sectionTitle = findSectionTitle(sentence);
        
        if (sectionTitle && currentSection.length > 0 && sectionTitle !== currentTitle) {
          // Add the current section to markdown sections
          markdownSections.push(`## ${currentTitle}\n\n${formatParagraphWithHighlights(currentSection.join(' '))}`);
          
          // Start a new section
          currentSection = [sentence];
          currentTitle = sectionTitle;
        } else {
          // Continue current section
          currentSection.push(sentence);
        }
        
        // Handle the last section
        if (index === sentences.length - 1 && currentSection.length > 0) {
          markdownSections.push(`## ${currentTitle}\n\n${formatParagraphWithHighlights(currentSection.join(' '))}`);
        }
      });
      
      return markdownSections.join('\n\n');
    }
  };
  
  const formatParagraphWithHighlights = (paragraph: string): string => {
    // Highlight financial numbers and metrics using markdown syntax
    return paragraph
      // Bold important financial figures
      .replace(/(\$[\d,.]+|[\d,.]+%|[\d,.]+ million|[\d,.]+ billion)/g, '**$1**')
      // Highlight trends with appropriate formatting
      .replace(/(increased|decreased|grew|declined|rose|fell) by (\d+%|\$[\d,.]+)/gi, '$1 by **$2**')
      // Add bullet points for lists that might be embedded in paragraphs
      .replace(/(?:\r\n|\r|\n)(\d+\.\s)/g, '\n* ')
      // Highlight important terms
      .replace(/(ROI|ROE|EBITDA|EPS|P\/E ratio|quarterly|annually|fiscal year|Q[1-4]|FY\d{4})/g, '_$1_');
  };
  
  // Custom components for rendering markdown with tailwind classes
  const MarkdownComponents = {
    h1: (props: any) => <h1 {...props} className="text-2xl font-bold text-purple-300 mb-3 mt-6" />,
    h2: (props: any) => <h2 {...props} className="text-xl font-semibold text-purple-300 mb-2 mt-5" />,
    h3: (props: any) => <h3 {...props} className="text-lg font-semibold text-purple-300 mb-2 mt-4" />,
    p: (props: any) => <p {...props} className="text-gray-200 leading-relaxed mb-3" />,
    strong: (props: any) => <span {...props} className="text-purple-300 font-semibold" />,
    em: (props: any) => <span {...props} className="text-blue-300 italic" />,
    ul: (props: any) => <ul {...props} className="list-disc pl-5 mb-3 text-gray-200" />,
    ol: (props: any) => <ol {...props} className="list-decimal pl-5 mb-3 text-gray-200" />,
    li: (props: any) => <li {...props} className="mb-1" />,
    blockquote: (props: any) => <blockquote {...props} className="border-l-4 border-gray-500 pl-4 italic text-gray-300 my-3" />,
    hr: (props: any) => <hr {...props} className="border-gray-700 my-4" />
  };
  
  // Render the empty state if no story
  if (!story) {
    return (
      <div className="text-gray-400 italic">
        No financial analysis available yet.
      </div>
    );
  }
  
  return (
    <div className="financial-story">
      <ReactMarkdown components={MarkdownComponents}>
        {markdownStory}
      </ReactMarkdown>
    </div>
  );
}