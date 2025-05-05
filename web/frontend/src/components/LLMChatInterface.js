import React, { useState, useEffect, useRef } from 'react';
import { llmApi } from '../services/api';

const LLMChatInterface = ({ designId, projectId, onSuggestionApply }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch conversation history when component mounts
  useEffect(() => {
    if (designId) {
      fetchConversationHistory();
    }
  }, [designId]);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversationHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await llmApi.getConversation(designId);
      setMessages(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch conversation history', err);
      setError('Failed to load conversation history. Please try again.');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Send message to LLM API
      const response = await llmApi.processInteraction({
        design_id: designId,
        project_id: projectId,
        message: input,
      });

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.data.message,
        created_at: new Date().toISOString(),
        design_changes: response.data.design_changes,
        suggestions: response.data.suggestions,
        questions: response.data.questions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setLoading(false);
    } catch (err) {
      console.error('Error sending message to LLM', err);
      setError('Failed to send message. Please try again.');
      setLoading(false);
    }
  };

  const handleApplySuggestion = (changes) => {
    if (onSuggestionApply && changes) {
      onSuggestionApply(changes);
    }
  };

  // Helper function to format timestamps
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return '';
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-blue-600 text-white">
        <h3 className="text-lg font-medium">Design Assistant</h3>
        <p className="text-sm text-blue-100">Ask for design improvements or suggestions</p>
      </div>

      {/* Messages area */}
      <div className="flex-1 p-4 overflow-y-auto">
        {loading && messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-gray-500">Loading conversation...</span>
          </div>
        ) : error && messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-red-500">
            <span>{error}</span>
            <button
              onClick={fetchConversationHistory}
              className="ml-2 text-blue-500 hover:text-blue-700 underline"
            >
              Retry
            </button>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mb-3 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <p className="text-center">
              No messages yet. Start a conversation with the Design Assistant to get suggestions
              and improvements for your packaging design.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3/4 rounded-lg px-4 py-2 ${message.role === 'user'
                    ? 'bg-blue-100 text-blue-900'
                    : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="mb-1">
                    <span className="font-medium">
                      {message.role === 'user' ? 'You' : 'Design Assistant'}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {formatTime(message.created_at)}
                    </span>
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>

                  {/* Design changes and suggestions */}
                  {message.role === 'assistant' && message.design_changes && (
                    <div className="mt-2 p-2 border border-blue-200 rounded bg-blue-50">
                      <div className="font-medium text-blue-700 mb-1">Suggested Changes:</div>
                      <ul className="text-sm">
                        {Object.entries(message.design_changes).map(([key, value]) => (
                          <li key={key} className="mb-1">
                            <span className="font-medium">{key}:</span> {value}
                          </li>
                        ))}
                      </ul>
                      <button
                        onClick={() => handleApplySuggestion(message.design_changes)}
                        className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                      >
                        Apply Changes
                      </button>
                    </div>
                  )}

                  {/* Suggestions */}
                  {message.role === 'assistant' && message.suggestions && message.suggestions.length > 0 && (
                    <div className="mt-2">
                      <div className="font-medium text-gray-700">Suggestions:</div>
                      <ul className="text-sm list-disc pl-5">
                        {message.suggestions.map((suggestion, i) => (
                          <li key={i}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Questions */}
                  {message.role === 'assistant' && message.questions && message.questions.length > 0 && (
                    <div className="mt-2">
                      <div className="font-medium text-gray-700">Questions:</div>
                      <ul className="text-sm list-disc pl-5">
                        {message.questions.map((question, i) => (
                          <li key={i}>{question}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your design..."
            className="flex-1 rounded-l-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            className="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            disabled={loading || !input.trim()}
          >
            {loading ? (
              <span className="flex items-center">
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Sending...
              </span>
            ) : (
              'Send'
            )}
          </button>
        </form>
        {error && <p className="mt-2 text-red-500 text-sm">{error}</p>}
      </div>
    </div>
  );
};

export default LLMChatInterface;