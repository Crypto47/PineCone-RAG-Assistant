import React, { useState, useEffect, useRef } from 'react';
import SendIcon from '@mui/icons-material/Send';
import ChatIcon from '@mui/icons-material/Chat';
import './Chat.css'; // Import external CSS file

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    // Add the user's message to the chat.
    const newMessage = {
      text: inputMessage,
      isBot: false,
      id: Date.now(),
    };

    setMessages(prev => [...prev, newMessage]);
    const currentInput = inputMessage;
    setInputMessage('');

    try {
      // Send the user's message to the /chat endpoint.
        const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput }),
      });

      // Check if the response is ok (status in the range 200-299)
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }

      const data = await response.json();

      // Check if the response contains the expected property.
      if (!data || !data.response) {
        throw new Error('No valid response from the chat endpoint.');
      }

      // Display the bot's response.
      const botResponse = {
        text: data.response,
        isBot: true,
        id: Date.now() + 1,
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      // Display an error message on screen.
      const errorMessage = {
        text: 'Sorry, an error occurred: ' + error.message,
        isBot: true,
        id: Date.now() + 1,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <ChatIcon className="chat-icon" />
        <h2>Chatbot</h2>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isBot ? 'bot' : 'user'}`}>
            <div className="message-content">
              {message.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message here..."
        />
        <button type="submit">
          <SendIcon className="send-icon" />
        </button>
      </form>
    </div>
  );
};

export default Chat;
