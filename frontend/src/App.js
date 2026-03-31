import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadMessages() {
      const response = await fetch('https://chatbot-production-6202.up.railway.app/messages');
      const data = await response.json();
      setMessages(data.messages);
    }
    loadMessages();
  }, []);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    const response = await fetch(`https://chatbot-production-6202.up.railway.app/chat?user_message=${encodeURIComponent(input)}`, {
      method: 'POST'
    });
    const data = await response.json();
    const aiMessage = { role: 'assistant', content: data.response };
    setMessages(prev => [...prev, aiMessage]);
    setLoading(false);
  }

  return (
    <div className="app">
      <div className="header">
        <h1>📈 Stock Market Assistant</h1>
        <p>Ask me anything about investing and the stock market</p>
      </div>

      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <span className="message-label">
              {msg.role === 'user' ? 'You' : 'Claude'}
            </span>
            <div className="message-bubble">
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {loading && (
          <div className="typing-indicator">
            Claude is thinking...
          </div>
        )}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about stocks, investing, markets..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;