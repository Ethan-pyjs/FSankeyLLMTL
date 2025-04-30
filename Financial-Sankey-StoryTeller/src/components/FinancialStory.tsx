import { useEffect, useState } from 'react';

interface FinancialStoryProps {
  story: string;
}

export default function FinancialStory({ story }: FinancialStoryProps) {
  const [formattedStory, setFormattedStory] = useState<React.ReactNode[]>([]);
  
  useEffect(() => {
    if (!story) return;
    
    // Format the story into sections
    formatStory(story);
  }, [story]);
  
  const formatStory = (storyText: string) => {
    // Split the story into logical sections
    // Look for patterns like section titles, numerical insights, etc.
    
    // Pattern matching for common financial analysis sections
    const sections = [];
    
    // Try to identify sections and format them
    let paragraphs = storyText.split('\n\n');
    
    // If there are no paragraph breaks, try to split by sentences
    if (paragraphs.length <= 1) {
      // Split by sentences and group into logical paragraphs
      const sentences = storyText.match(/[^.!?]+[.!?]+/g) || [];
      
      // Group sentences into logical sections
      const formattedSections: { title: string; content: string }[] = [];
      
      // Group related sentences into sections based on keywords
      let currentSection: string[] = [];
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
      
      // Helper to find the section title for a sentence
      const findSectionTitle = (sentence: string) => {
        for (const { pattern, title } of keywordPatterns) {
          if (pattern.test(sentence)) {
            return title;
          }
        }
        return null;
      };
      
      // Process sentences into sections
      let currentTitle = "Overview"; // Default title
      
      sentences.forEach((sentence, index) => {
        // Check if this sentence should start a new section
        const sectionTitle = findSectionTitle(sentence);
        
        if (sectionTitle && currentSection.length > 0 && sectionTitle !== currentTitle) {
          // Start a new section
          formattedSections.push({
            title: currentTitle,
            content: currentSection.join(' ')
          });
          currentSection = [sentence];
          currentTitle = sectionTitle;
        } else {
          // Continue current section
          currentSection.push(sentence);
        }
        
        // Handle the last section
        if (index === sentences.length - 1 && currentSection.length > 0) {
          formattedSections.push({
            title: currentTitle,
            content: currentSection.join(' ')
          });
        }
      });
      
      // Convert sections to JSX
      formattedSections.forEach(section => {
        sections.push(
          <div key={section.title} className="mb-4">
            <h3 className="text-lg font-semibold text-purple-300 mb-2">{section.title}</h3>
            <p className="text-gray-200 leading-relaxed">{section.content}</p>
          </div>
        );
      });
    } else {
      // Use existing paragraph breaks
      paragraphs.forEach((paragraph, index) => {
        // Try to determine if this is a header or section title
        if (paragraph.length < 50 && (paragraph.endsWith(':') || paragraph.toUpperCase() === paragraph)) {
          // This is likely a header
          sections.push(
            <h3 key={`header-${index}`} className="text-lg font-semibold text-purple-300 mt-4 mb-2">
              {paragraph.replace(':', '')}
            </h3>
          );
        } else {
          // This is a regular paragraph
          sections.push(
            <p key={`para-${index}`} className="text-gray-200 leading-relaxed mb-3">
              {paragraph}
            </p>
          );
        }
      });
    }
    
    // If we couldn't identify sections, format as regular paragraphs with highlights
    if (sections.length === 0) {
      // Fallback: Format as a single block with highlighted numbers
      const highlightedText = storyText.replace(
        /(\$[\d,.]+|[\d,.]+%|[\d,.]+ million|[\d,.]+ billion)/g, 
        '<span class="text-purple-300 font-semibold">$1</span>'
      );
      
      sections.push(
        <div key="fallback" 
          className="text-gray-200 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: highlightedText }}
        />
      );
    }
    
    setFormattedStory(sections);
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
      {formattedStory}
    </div>
  );
}