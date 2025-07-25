import React from 'react';
import { HeartIcon, InformationCircleIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/button';

interface ChatHeaderProps {
  onInfoClick?: () => void;
}

export function ChatHeader({ onInfoClick }: ChatHeaderProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-blue-600 rounded-full flex items-center justify-center">
            <HeartIcon className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Cogitto AI Assistant</h1>
            <p className="text-sm text-gray-700 font-medium">Powered by real FDA data & AI</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onInfoClick}
          className="text-gray-600 hover:text-gray-800"
        >
          <InformationCircleIcon className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
