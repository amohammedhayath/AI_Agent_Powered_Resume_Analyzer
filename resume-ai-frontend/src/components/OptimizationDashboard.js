import React, { useState } from 'react';
import axios from 'axios';
import './OptimizationDashboard.css'; // <--- Import the styles we just made

const OptimizationDashboard = ({ matchId }) => {
    const [suggestions, setSuggestions] = useState([]);
    const [status, setStatus] = useState('IDLE'); // 'IDLE', 'PROCESSING', 'COMPLETED'
    
    const startOptimization = async () => {
        try {
            setStatus('PROCESSING');
            await axios.post('http://127.0.0.1:8000/api/optimize/trigger/', { match_id: matchId });
            pollForResults();
        } catch (error) {
            console.error(error);
            setStatus('ERROR');
        }
    };

    const pollForResults = () => {
        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`http://127.0.0.1:8000/api/optimize/${matchId}/results/`);
                if (res.data.status === 'COMPLETED' && res.data.data.length > 0) {
                    setSuggestions(res.data.data);
                    setStatus('COMPLETED');
                    clearInterval(interval);
                }
            } catch (err) {
                console.error(err);
            }
        }, 2000);
    };

    return (
        <div className="mt-5">
            {/* Header Section */}
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h4 className="fw-bold mb-0" style={{ color: '#2c3e50' }}>
                    ✨ AI Resume Enhancer
                </h4>
                
                {status === 'IDLE' && (
                    <button 
                        className="btn btn-dark rounded-pill px-4 py-2 shadow-sm" 
                        onClick={startOptimization}
                        style={{ transition: 'all 0.3s' }}
                    >
                        Generate Improvements
                    </button>
                )}
                
                {status === 'PROCESSING' && (
                    <div className="d-flex align-items-center text-primary bg-white px-3 py-2 rounded-pill shadow-sm">
                        <div className="spinner-border spinner-border-sm me-2" role="status"></div>
                        <span className="fw-bold small">Crafting suggestions...</span>
                    </div>
                )}
            </div>

            {/* Suggestions List */}
            {suggestions.map((item, index) => (
                <div key={index} className="glass-panel p-4">
                    <div className="mb-3">
                        <span className="category-badge">{item.category} Update</span>
                    </div>
                    
                    <div className="diff-grid">
                        {/* Left: Original */}
                        <div>
                            <h6 className="text-uppercase text-danger small fw-bold mb-2">🔴 Original</h6>
                            <div className="original-box">
                                "{item.original_text}"
                            </div>
                        </div>

                        {/* Center: Arrow */}
                        <div className="arrow-container">
                            ➜
                        </div>

                        {/* Right: Optimized */}
                        <div>
                            <h6 className="text-uppercase text-success small fw-bold mb-2">🟢 AI Optimized</h6>
                            <div className="optimized-box">
                                "{item.optimized_text}"
                            </div>
                        </div>
                    </div>

                    {/* Footer: Reasoning */}
                    <div className="reason-text">
                        <strong>💡 Why:</strong> {item.reason}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default OptimizationDashboard;