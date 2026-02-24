/**
 * useAIChat Hook - Minimal Working Version
 */

import { useState, useCallback, useRef } from 'react';
import type { ChatMessage } from '../../types/ai';

export interface UseAIChatReturn {
  messages: ChatMessage[];
  input: string;
  isLoading: boolean;
  error: string | null;
  suggestions: string[];
  isListening: boolean;
  setInput: (input: string) => void;
  sendMessage: (content?: string) => Promise<void>;
  clearChat: () => void;
  startVoiceInput: () => void;
  stopVoiceInput: () => void;
}

const defaultSuggestions = [
  "What's my revenue today?",
  "Show me insights for this week",
  "Any gaps in today's schedule?",
  "Predict my weekend bookings",
];

export const useAIChat = (_options?: { context?: string }): UseAIChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  const sendMessage = useCallback(async (content?: string) => {
    const messageContent = content || input;
    if (!messageContent.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: `I received your message: "${messageContent}". This is a simulated response for Task 2.6 implementation.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  }, [input, isLoading]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  const startVoiceInput = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Voice input is not supported in this browser');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-IN';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0])
        .map((result: any) => result.transcript)
        .join('');
      setInput(transcript);
    };

    recognition.onerror = (event: any) => {
      setError(`Voice input error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, []);

  const stopVoiceInput = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  return {
    messages,
    input,
    isLoading,
    error,
    suggestions: defaultSuggestions,
    isListening,
    setInput,
    sendMessage,
    clearChat,
    startVoiceInput,
    stopVoiceInput,
  };
};

export default useAIChat;
