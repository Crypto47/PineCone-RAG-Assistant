import React from 'react';
import Chat from './Chat'; // Adjust the path based on your file structure
import './Chat.css'; // Import the CSS file

function App() {
  return (
    <div className="App">
      {/* Optional header */}
      {/* <header className="App-header">
        <h1>ChatGPT Clone</h1>
      </header> */}

      <main>
        <Chat />
      </main>
    </div>
  );
}

export default App;