'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { authService } from '@/services/auth';
import { chatService, ChatMessageResponse } from '@/services/chat';
import { ChatBubble } from '@/components/chat/ChatBubble';
import { TypingIndicator } from '@/components/chat/TypingIndicator';
import { ChatInput } from '@/components/chat/ChatInput';
import { QuickSuggestions } from '@/components/chat/QuickSuggestions';
import { ChatHeader } from '@/components/chat/ChatHeader';
import { SafetyDisclaimer } from '@/components/chat/SafetyDisclaimer';
import { Button } from '@/components/ui/button';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import Link from 'next/link';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  mentioned_medications?: string[];
  risk_level?: 'low' | 'medium' | 'high' | 'critical';
  ai_model?: string;
  confidence_score?: number;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => `cogitto_session_${Date.now()}`);
  const [conversationId, setConversationId] = useState<string>('');
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showDisclaimer, setShowDisclaimer] = useState(true);

  // Check authentication and show welcome message
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Add welcome message immediately
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      role: 'assistant',
      content: `👋 **Welcome to Cogitto AI!**

I'm your intelligent medication assistant powered by real FDA data and advanced AI. I can help you with:

- **Drug interactions** - "Can I take ibuprofen with warfarin?"
- **Medication information** - "Tell me about aspirin"
- **Side effects** - "What are the side effects of lisinopril?"
- **Safety guidance** - "Is it safe to take these together?"

What would you like to know about your medications today?`,
      timestamp: new Date().toISOString(),
      risk_level: 'low'
    };

    setMessages([welcomeMessage]);
    console.log('🎉 Chat ready with session ID:', sessionId);
  }, [router, sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageContent: string) => {
    // Add user message immediately
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      console.log('🚀 Sending message to AI backend...');
      
      // Send message directly to backend
      const response: ChatMessageResponse = await chatService.sendMessage({
        message: messageContent,
        session_id: sessionId,
        conversation_id: conversationId || undefined
      });

      // Mark backend as connected (for internal tracking)
      if (!isBackendConnected) {
        setIsBackendConnected(true);
        console.log('✅ AI backend connected successfully!');
      }

      // Update conversation ID if we got a new one
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Create AI response message from backend
      const aiMessage: ChatMessage = {
        id: response.assistant_response.id,
        role: 'assistant',
        content: response.assistant_response.content,
        timestamp: response.assistant_response.timestamp,
        mentioned_medications: response.cogitto_insights.mentioned_medications,
        risk_level: mapRiskLevel(response.assistant_response.risk_level),
        ai_model: response.assistant_response.ai_model,
        confidence_score: response.assistant_response.confidence_score
      };

      setMessages(prev => [...prev, aiMessage]);
      console.log(`✅ Real AI response from ${response.assistant_response.ai_model}`);

    } catch (error: any) {
      console.error('❌ Backend AI failed, using fallback:', error);
      
      // Fallback to mock response
      const mockResponse = generateMockResponse(messageContent);
      
      const aiMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        role: 'assistant',
        content: mockResponse.content + '\n\n*Note: Currently in offline mode.*',
        timestamp: new Date().toISOString(),
        mentioned_medications: mockResponse.medications,
        risk_level: mockResponse.risk_level,
        ai_model: 'cogitto-fallback'
      };

      setMessages(prev => [...prev, aiMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // Mock response generator for fallback
  const generateMockResponse = (message: string) => {
    const messageLower = message.toLowerCase();
    
    if (messageLower.includes('ibuprofen') && messageLower.includes('warfarin')) {
      return {
        content: `⚠️ **MAJOR INTERACTION FOUND**

There is a significant interaction between **ibuprofen** and **warfarin**. This combination increases bleeding risk due to antiplatelet effects.

🚨 **Recommendation**: Avoid this combination. Use acetaminophen instead for pain relief.

**Important**: Please consult your healthcare provider immediately about this interaction.`,
        medications: ['ibuprofen', 'warfarin'],
        risk_level: 'high' as const
      };
    }
    
    return {
      content: `I understand you're asking about "${message}". I can help with medication information, drug interactions, side effects, and safety guidance.

💡 **Try asking**:
- "What is [medication name] used for?"
- "Can I take [med1] with [med2]?"
- "What are the side effects of [medication]?"

What specific medication question can I help you with?`,
      medications: [],
      risk_level: 'low' as const
    };
  };

  const mapRiskLevel = (backendRiskLevel: string): 'low' | 'medium' | 'high' | 'critical' => {
    const riskMap: { [key: string]: 'low' | 'medium' | 'high' | 'critical' } = {
      'low': 'low',
      'medium': 'medium', 
      'high': 'high',
      'critical': 'critical'
    };
    return riskMap[backendRiskLevel.toLowerCase()] || 'low';
  };

  const handleInfoClick = () => {
    setShowDisclaimer(!showDisclaimer);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="flex-shrink-0">
        <ChatHeader onInfoClick={handleInfoClick} />
      </div>

      {/* Back Button */}
      <div className="flex-shrink-0 px-4 py-2 bg-white border-b border-gray-200">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm" className="text-gray-700 hover:text-gray-900 font-medium">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      {/* Safety Disclaimer */}
      {showDisclaimer && (
        <div className="flex-shrink-0">
          <SafetyDisclaimer />
        </div>
      )}

      {/* Quick Suggestions */}
      {messages.length <= 1 && !isTyping && (
        <div className="flex-shrink-0">
          <QuickSuggestions 
            onSuggestionClick={handleSendMessage}
            disabled={isTyping}
          />
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-4">
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          
          {isTyping && <TypingIndicator />}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      <div className="flex-shrink-0">
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isTyping}
          placeholder="Ask about medications, interactions, side effects..."
        />
      </div>
    </div>
  );
}
