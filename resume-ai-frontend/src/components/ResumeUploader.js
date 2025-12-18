import React, { useState } from 'react';
import axios from 'axios';

const ResumeUploader = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [message, setMessage] = useState('');
    const [uploading, setUploading] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setStatus('');
        setMessage('');
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Please select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        setStatus('info');
        setMessage('Uploading...');

        try {
            // 1. Send File to Django
            const response = await axios.post('http://127.0.0.1:8000/api/resumes/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setStatus('success');
            setMessage(`Upload Successful! ID: ${response.data.id}`);

            // Pass the Resume ID up to the parent component (App.js)
            if(onUploadSuccess) {
                onUploadSuccess(response.data.id);
            }

        } catch (error) {
            console.error(error);
            setStatus('danger');
            setMessage('Upload failed. Check console for details.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="card shadow-sm mb-4">
            <div className="card-header bg-primary text-white">
                <h5 className="mb-0">Step 1: Upload Resume</h5>
            </div>
            <div className="card-body">
                <div className="mb-3">
                    <input
                        type="file"
                        className="form-control"
                        accept=".pdf"
                        onChange={handleFileChange}
                    />
                </div>

                <button
                    className="btn btn-primary w-100"
                    onClick={handleUpload}
                    disabled={uploading}
                >
                    {uploading ? 'Uploading...' : 'Upload Resume'}
                </button>

                {message && (
                    <div className={`alert alert-${status} mt-3`}>
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumeUploader;