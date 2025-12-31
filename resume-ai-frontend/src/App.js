import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css'; // Import the new styles
import ResumeUploader from './components/ResumeUploader';
import JobAnalyzer from './components/JobAnalyzer';

function App() {
  const [resumeId, setResumeId] = useState(null);

  return (
    <div className="app-container">
      {/* Header */}
      <div className="text-center mb-5">
        <h1 className="display-4 mb-2">🚀 AI Resume Agent</h1>
        <p className="lead text-white-50">
          Intelligent Matching & Semantic Optimization
        </p>
      </div>

      {/* Step 1: Upload (Always Visible) */}
      <div className="glass-card">
        <ResumeUploader onUploadSuccess={(id) => setResumeId(id)} />
      </div>

      {/* Step 2: Analysis (Only if resume uploaded) */}
      {resumeId && (
        <div className="glass-card animate__animated animate__fadeInUp">
           <JobAnalyzer resumeId={resumeId} />
        </div>
      )}
      
      {/* Footer */}
      <div className="text-center mt-5 text-white-50 small">
        <p>Powered by Gemini 1.5 Flash & Vector Search</p>
      </div>
    </div>
  );
}

export default App;