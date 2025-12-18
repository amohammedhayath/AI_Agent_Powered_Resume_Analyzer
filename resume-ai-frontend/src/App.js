import React, { useState } from 'react';
import ResumeUploader from './components/ResumeUploader';
import JobAnalyzer from './components/JobAnalyzer';

function App() {
  const [resumeId, setResumeId] = useState(null);

  return (
    <div className="container py-5">
      <h1 className="text-center mb-5">🚀 AI Resume Analyzer</h1>

      <div className="row">
        {/* Left Column: Upload */}
        <div className="col-md-5">
          <ResumeUploader onUploadSuccess={(id) => setResumeId(id)} />
        </div>

        {/* Right Column: Analyze */}
        <div className="col-md-7">
          <div className={!resumeId ? "opacity-50" : ""}>
             <JobAnalyzer resumeId={resumeId} />
          </div>
          {!resumeId && (
            <p className="text-center text-muted mt-2">
              (Upload a resume to unlock the Job Analyzer)
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;