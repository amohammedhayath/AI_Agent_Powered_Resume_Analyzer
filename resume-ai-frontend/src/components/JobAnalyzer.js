import React, { useState, useEffect } from 'react';
import axios from 'axios';

const JobAnalyzer = ({ resumeId }) => {
    const [jobDescription, setJobDescription] = useState('');
    const [title, setTitle] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState('');

    const handleAnalyze = async () => {
        if (!resumeId) {
            alert("Please upload a resume first!");
            return;
        }

        setAnalyzing(true);
        setResult(null);

        try {
            // 1. Start Analysis
            const response = await axios.post('http://127.0.0.1:8000/api/jobs/analyze/', {
                resume_id: resumeId,
                title: title || "Frontend Job Search",
                description: jobDescription
            });

            const jobId = response.data.job_id;
            setStatus('Thinking...');

            // 2. Poll for Results every 2 seconds
            pollForResult(jobId);

        } catch (error) {
            console.error(error);
            setAnalyzing(false);
            alert("Analysis failed to start.");
        }
    };

    const pollForResult = (jobId) => {
        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`http://127.0.0.1:8000/api/jobs/${jobId}/result/`);

                if (res.data.status === "COMPLETED") {
                    clearInterval(interval);
                    setResult(res.data);
                    setAnalyzing(false);
                    setStatus('');
                }
            } catch (err) {
                console.error("Polling error", err);
            }
        }, 2000); // Check every 2 seconds
    };

    return (
        <div className="card shadow-sm">
            <div className="card-header bg-success text-white">
                <h5 className="mb-0">Step 2: Job Match</h5>
            </div>
            <div className="card-body">
                <div className="mb-3">
                    <input
                        type="text"
                        className="form-control mb-2"
                        placeholder="Job Title (e.g. Python Dev)"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                    <textarea
                        className="form-control"
                        rows="5"
                        placeholder="Paste Job Description here..."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                    ></textarea>
                </div>

                <button
                    className="btn btn-success w-100"
                    onClick={handleAnalyze}
                    disabled={analyzing || !resumeId}
                >
                    {analyzing ? `Analyzing... (${status})` : 'Analyze Match'}
                </button>

                {/* --- RESULTS DISPLAY --- */}
                {result && (
                    <div className="mt-4 p-3 border rounded bg-light">
                        <div className="text-center">
                            <h2 className={`display-4 fw-bold ${result.score > 70 ? 'text-success' : 'text-danger'}`}>
                                {result.score}%
                            </h2>
                            <p className="text-muted">Match Score</p>
                        </div>
                        <hr />
                        <p><strong>AI Verdict:</strong></p>
                        <p className="fst-italic">"{result.justification}"</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default JobAnalyzer;