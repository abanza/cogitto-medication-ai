import React from 'react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { ExclamationTriangleIcon, HeartIcon } from '@heroicons/react/24/outline';

interface ChatBubbleProps {
  message: {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: string;
    mentioned_medications?: string[];
    risk_level?: 'low' | 'medium' | 'high' | 'critical';
  };
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';
  
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'bg-red-100 border-red-300 text-red-800';
      case 'high': return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'medium': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      default: return 'bg-blue-100 border-blue-300 text-blue-800';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Function to render formatted text
  const renderFormattedText = (text: string) => {
    // Handle bold text **text**
    const boldRegex = /\*\*(.*?)\*\*/g;
    let parts = text.split(boldRegex);
    
    return parts.map((part, index) => {
      // Every odd index is bold text (captured groups)
      if (index % 2 === 1) {
        return (
          <strong key={index} className={cn(
            "font-bold",
            isUser ? "text-white" : "text-gray-900"
          )}>
            {part}
          </strong>
        );
      }
      return part;
    });
  };

  // Function to format message content
  const formatContent = (content: string) => {
    const lines = content.split('\n');
    const formattedLines: JSX.Element[] = [];
    
    lines.forEach((line, lineIndex) => {
      if (!line.trim()) {
        // Empty line - add spacing
        formattedLines.push(<div key={lineIndex} className="h-2" />);
        return;
      }
      
      // Remove quotes if they wrap the entire line
      let cleanLine = line.trim();
      if (cleanLine.startsWith('"') && cleanLine.endsWith('"')) {
        cleanLine = cleanLine.slice(1, -1);
      }
      
      // Check for bullet points
      if (cleanLine.startsWith('• ')) {
        const bulletText = cleanLine.slice(2);
        formattedLines.push(
          <div key={lineIndex} className="flex items-start mb-2">
            <span className={cn("mr-2 text-sm mt-0.5 font-medium", isUser ? "text-white" : "text-gray-800")}>•</span>
            <span className={cn("text-sm leading-relaxed", isUser ? "text-white" : "text-gray-900")}>
              {renderFormattedText(bulletText)}
            </span>
          </div>
        );
        return;
      }
      
      // Check for warning/info lines (starting with emojis)
      if (cleanLine.match(/^[⚠️🚨✅ℹ️💊💡👋]/)) {
        formattedLines.push(
          <div key={lineIndex} className={cn(
            "text-sm mb-3 font-semibold",
            isUser ? "text-white" : "text-gray-900"
          )}>
            {renderFormattedText(cleanLine)}
          </div>
        );
        return;
      }
      
      // Regular text paragraph
      if (cleanLine.trim()) {
        formattedLines.push(
          <p key={lineIndex} className={cn(
            "text-sm mb-2 last:mb-0 leading-relaxed",
            isUser ? "text-white" : "text-gray-900"
          )}>
            {renderFormattedText(cleanLine)}
          </p>
        );
      }
    });
    
    return formattedLines;
  };

  return (
    <div className={cn('flex w-full mb-4', isUser ? 'justify-end' : 'justify-start')}>
      <div className={cn('max-w-[85%] space-y-2')}>
        {/* Avatar and Name */}
        <div className={cn('flex items-center space-x-2', isUser ? 'flex-row-reverse space-x-reverse' : '')}>
          <div className={cn(
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
            isUser ? 'bg-teal-600 text-white' : 'bg-blue-600 text-white'
          )}>
            {isUser ? 'You' : <HeartIcon className="h-4 w-4" />}
          </div>
          <span className="text-xs text-gray-600 font-medium">
            {isUser ? 'You' : 'Cogitto AI'} • {formatTime(message.timestamp)}
          </span>
        </div>

        {/* Message Bubble */}
        <div className={cn(
          'rounded-2xl px-4 py-3 shadow-sm',
          isUser 
            ? 'bg-teal-600 text-white rounded-br-md' 
            : 'bg-white border border-gray-200 rounded-bl-md'
        )}>
          {/* Risk Level Indicator for AI Messages */}
          {isAssistant && message.risk_level && message.risk_level !== 'low' && (
            <div className={cn(
              'flex items-center space-x-2 px-3 py-2 rounded-lg mb-3 text-sm font-semibold border',
              getRiskColor(message.risk_level)
            )}>
              <ExclamationTriangleIcon className="h-4 w-4" />
              <span className="capitalize">{message.risk_level} Priority</span>
            </div>
          )}

          {/* Formatted Message Content */}
          <div className="space-y-1">
            {formatContent(message.content)}
          </div>

          {/* Mentioned Medications */}
          {message.mentioned_medications && message.mentioned_medications.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {message.mentioned_medications.map((med, index) => (
                <Badge key={index} variant="medical" className="text-xs">
                  💊 {med}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
