import React from 'react';
import { Button } from '@/components/ui/button';

interface QuickSuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
  disabled?: boolean;
}

export function QuickSuggestions({ onSuggestionClick, disabled = false }: QuickSuggestionsProps) {
  const suggestions = [
    "Can I take ibuprofen with warfarin?",
    "What is acetaminophen used for?",
    "Tell me about aspirin for heart health",
    "Are there interactions with my medications?",
    "What are the side effects of lisinopril?",
    "Is it safe to take Tylenol and Advil together?"
  ];

  return (
    <div className="p-4 bg-gray-50 border-b border-gray-200">
      <h3 className="text-sm font-semibold text-gray-800 mb-3">💡 Quick Questions</h3>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            disabled={disabled}
            onClick={() => onSuggestionClick(suggestion)}
            className="text-xs text-gray-900 hover:text-gray-900 border-gray-300 hover:border-gray-400 font-medium"
          >
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
}
