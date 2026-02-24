import React, { useState, useRef, useEffect } from 'react';
import { Button, Input, Badge } from '@salon-flow/ui';
import { 
  MessageSquare,
  Send,
  Bot,
  User,
  Sparkles,
  Calendar,
  Users,
  DollarSign,
  Clock,
  AlertCircle,
  Lightbulb,
  RefreshCw,
  Loader2,
} from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: Array<{
    label: string;
    action: string;
    data?: any;
  }>;
  suggestions?: string[];
}

interface SuggestedPrompt {
  text: string;
  icon: React.ElementType;
  category: string;
}

const suggestedPrompts: SuggestedPrompt[] = [
  { text: "Show today's bookings", icon: Calendar, category: 'Bookings' },
  { text: "What's my revenue this week?", icon: DollarSign, category: 'Analytics' },
  { text: 'Who are my top customers?', icon: Users, category: 'Customers' },
  { text: 'Any staff on leave today?', icon: Clock, category: 'Staff' },
  { text: 'Suggest ways to increase revenue', icon: Lightbulb, category: 'Insights' },
  { text: 'Show pending payments', icon: AlertCircle, category: 'Payments' },
];

const AIChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI assistant. I can help you manage your salon, analyze performance, and provide insights. How can I assist you today?",
      timestamp: new Date(),
      suggestions: [
        "Show today's appointments",
        "What's my revenue trend?",
        'Any customer feedback?',
      ],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const handlePromptClick = (prompt: string) => {
    setInputValue(prompt);
    inputRef.current?.focus();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setStreamingMessage('');

    try {
      // Simulate streaming response
      const responses: Record<string, string> = {
        'bookings': `**Today's Bookings Overview**

You have **12 appointments** scheduled for today:

- 9:00 AM - Haircut with Rahul (Chair 1)
- 10:00 AM - Hair Color with Priya (Chair 3)
- 11:30 AM - Bridal Makeup with Anjali (Bridal Room)
- 2:00 PM - Spa Treatment with Meera (Spa Room)

**Peak hours:** 10 AM - 12 PM
**Available slots:** 3:30 PM, 5:00 PM`,
        'revenue': `**Revenue Analysis**

**This Week:** Rs 45,230
**Last Week:** Rs 38,450
**Growth:** +17.6%

**Top Services:**
1. Hair Color - Rs 12,500
2. Bridal Package - Rs 10,000
3. Spa Treatments - Rs 8,200

**Recommendation:** Consider promoting spa packages on weekdays to increase mid-week revenue.`,
        'customers': `**Top Customers**

1. **Priya Sharma** - Rs 12,450 spent (15 visits)
   Favorite: Hair Color, Spa

2. **Anjali Reddy** - Rs 9,800 spent (12 visits)
   Favorite: Bridal Services

3. **Rahul Kumar** - Rs 7,200 spent (20 visits)
   Favorite: Haircut, Beard Trim

**Loyalty Insights:**
- 316 active members
- 45 customers with birthdays this month
- 12 memberships expiring soon`,
        'staff': `**Staff Status Today**

**Present (8/10):**
- Rahul, Priya, Meera, Suresh, Kavitha, Arun, Lakshmi, Venkat

**On Leave:**
- Srinivas (Sick leave)
- Divya (Personal)

**Performance Highlights:**
- Meera: Highest bookings this week (23)
- Rahul: Best customer rating (4.9/5)`,
        'payments': `**Pending Payments**

**Total Outstanding:** Rs 8,450

| Customer | Amount | Due Date | Status |
|----------|--------|----------|--------|
| K. Ramesh | Rs 2,500 | Feb 20 | Overdue |
| S. Priya | Rs 3,200 | Feb 22 | Due Soon |
| M. Lakshmi | Rs 2,750 | Feb 25 | Pending |

**Action Required:** Send payment reminders to 2 customers.`,
      };

      // Find matching response or use default
      let responseText = "I understand you're asking about your salon operations. Let me help you with that. Could you be more specific about what you'd like to know?";

      for (const [key, value] of Object.entries(responses)) {
        if (userMessage.content.toLowerCase().includes(key)) {
          responseText = value;
          break;
        }
      }

      // Simulate streaming
      const words = responseText.split(' ');
      for (let i = 0; i < words.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 30));
        setStreamingMessage(words.slice(0, i + 1).join(' '));
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseText,
        timestamp: new Date(),
        actions: [
          { label: 'View Details', action: 'view_details' },
          { label: 'Export Report', action: 'export' },
        ],
      };

      setMessages(prev => [...prev, assistantMessage]);
      setStreamingMessage('');
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = (action: string, data?: any) => {
    console.log('Action:', action, data);
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">AI Assistant</h1>
              <p className="text-sm text-gray-500">Powered by Gemini AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="success" size="sm">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                Online
              </span>
            </Badge>
            <Button variant="outline" size="sm" leftIcon={<RefreshCw className="h-4 w-4" />}>
              New Chat
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] ${message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200'} rounded-2xl px-4 py-3 shadow-sm`}>
              <div className="prose prose-sm max-w-none">
                {message.content.split('\n').map((line, i) => (
                  <React.Fragment key={i}>
                    {line}
                    {i < message.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>

              {/* Suggestions */}
              {message.suggestions && (
                <div className="mt-3 pt-3 border-t border-gray-100 space-y-2">
                  <p className="text-xs text-gray-500">Suggested follow-ups:</p>
                  <div className="flex flex-wrap gap-2">
                    {message.suggestions.map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => handlePromptClick(suggestion)}
                        className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              {message.actions && (
                <div className="mt-3 pt-3 border-t border-gray-100 flex gap-2">
                  {message.actions.map((action, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => handleAction(action.action, action.data)}
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              )}

              <div className={`mt-2 text-xs ${message.role === 'user' ? 'text-primary-200' : 'text-gray-400'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4 text-primary-600" />
              </div>
            )}
          </div>
        ))}

        {/* Streaming Message */}
        {streamingMessage && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center flex-shrink-0">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="max-w-[80%] bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
              <div className="prose prose-sm max-w-none">
                {streamingMessage}
                <span className="inline-block w-1 h-4 bg-primary-500 animate-pulse ml-1"></span>
              </div>
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && !streamingMessage && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center flex-shrink-0">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
                <span className="text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      {messages.length <= 2 && !isLoading && (
        <div className="px-4 pb-4">
          <p className="text-sm text-gray-500 mb-3">Suggested questions:</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {suggestedPrompts.map((prompt, index) => {
              const IconComponent = prompt.icon;
              return (
                <button
                  key={index}
                  onClick={() => handlePromptClick(prompt.text)}
                  className="flex items-center gap-2 p-3 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg text-left text-sm text-gray-700 transition-colors"
                >
                  <IconComponent className="h-4 w-4 text-primary-500 flex-shrink-0" />
                  <span className="line-clamp-1">{prompt.text}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything about your salon..."
            className="flex-1"
            leftIcon={<MessageSquare className="h-4 w-4" />}
            disabled={isLoading}
          />
          <Button
            type="submit"
            isLoading={isLoading}
            disabled={!inputValue.trim()}
            leftIcon={<Send className="h-4 w-4" />}
          >
            Send
          </Button>
        </form>
        <p className="mt-2 text-xs text-gray-400 text-center">
          AI responses are generated and may not always be accurate. Verify important information.
        </p>
      </div>
    </div>
  );
};

export default AIChatPage;
