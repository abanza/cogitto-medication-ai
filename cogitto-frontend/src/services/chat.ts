import api from '@/lib/api';

export interface ChatMessageRequest {
  message: string;
  session_id: string;
  conversation_id?: string;
}

export interface ChatMessageResponse {
  conversation_id: string;
  session_id: string;
  user_message: {
    id: string;
    role: string;
    content: string;
    timestamp: string;
    mentioned_medications?: string[];
  };
  assistant_response: {
    id: string;
    role: string;
    content: string;
    timestamp: string;
    risk_level: string;
    confidence_score: number;
    ai_model: string;
  };
  cogitto_insights: {
    mentioned_medications: string[];
    medication_insights: string[];
    safety_recommendations: string[];
    interaction_warnings: string[];
    followup_questions: string[];
    ai_processing: {
      model_used: string;
      confidence_score: number;
      processing_successful: boolean;
    };
  };
  disclaimer: string;
  session_context: {
    total_queries: number;
    current_medications: string[];
    overall_risk_level: string;
  };
}

export interface ChatSession {
  session_id: string;
  message: string;
  current_medications?: string[];
  instructions?: string;
}

export const chatService = {
  // Start a new chat session with correct backend format
  async startSession(currentMedications: string[] = []): Promise<ChatSession> {
    try {
      // Based on the error, the backend expects this format:
      const response = await api.post('/chat/start-session', {
        current_medications: currentMedications,
        user_id: null
      });
      return response.data;
    } catch (error: any) {
      console.error('Chat session start failed:', error.response?.data);
      throw error;
    }
  },

  // Send a message to the AI
  async sendMessage(request: ChatMessageRequest): Promise<ChatMessageResponse> {
    try {
      const response = await api.post('/chat/message', request);
      return response.data;
    } catch (error: any) {
      console.error('Chat message failed:', error.response?.data);
      throw error;
    }
  },

  // Get conversation history
  async getConversationHistory(conversationId: string) {
    try {
      const response = await api.get(`/chat/conversation/${conversationId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get conversation failed:', error.response?.data);
      throw error;
    }
  }
};
