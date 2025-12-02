import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import axios from 'axios'; // We use Axios for easy upload progress tracking

export default function Files() {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // You normally get this from URL params or a selector
  // For now, we hardcode it to match your "physics-101" class
  const activeClassId = "physics-101"; 

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("classroom_id", activeClassId);

    try {
        const token = localStorage.getItem('access_token');
        
        // ⚡ REAL UPLOAD with Progress
        const res = await axios.post('http://localhost:8000/api/files/upload', formData, {
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setUploadProgress(percentCompleted);
            }
        });

        if (res.data.success) {
            toast.success("File Uploaded Successfully!");
            setUploadProgress(0);
            setFiles(prev => [...prev, res.data.file]);
        }
    } catch (error) {
        console.error(error);
        toast.error("Upload Failed");
        setUploadProgress(0);
    }
  };

  const handleDownload = (fileId, fileName) => {
      // Direct browser download
      const link = document.createElement('a');
      link.href = `http://localhost:8000/api/files/download/${fileId}`;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
  };

  return (
    <div>
        <div style={{display:'flex', justifyContent:'space-between', marginBottom:'20px'}}>
            <h2>Class Resources</h2>
            <div style={{position:'relative'}}>
                <input type="file" onChange={handleUpload} style={{position:'absolute', opacity:0, width:'100%', height:'100%', cursor:'pointer'}} />
                <button className="btn btn-primary">Upload File</button>
            </div>
        </div>

        {/* Progress Bar */}
        {uploadProgress > 0 && (
            <div style={{width:'100%', background:'#333', height:'10px', borderRadius:'5px', marginBottom:'20px'}}>
                <div style={{width: `${uploadProgress}%`, background:'#16a34a', height:'100%', borderRadius:'5px', transition:'0.2s'}}></div>
            </div>
        )}

        {/* Files List */}
        <div className="card">
            {files.length === 0 && <p style={{color:'#666', padding:'10px'}}>No files uploaded yet.</p>}
            
            {files.map(file => (
                <div key={file.id} style={{padding:'15px', borderBottom:'1px solid #333', display:'flex', justifyContent:'space-between'}}>
                    <div style={{display:'flex', alignItems:'center', gap:'10px'}}>
                        <span style={{fontSize:'1.5rem'}}>📄</span>
                        <div>
                            <div>{file.name}</div>
                            <small style={{color:'#888'}}>{file.size}</small>
                        </div>
                    </div>
                    <div>
                        {file.offline ? 
                            <span style={{background:'#166534', padding:'4px 8px', borderRadius:'10px', fontSize:'0.8rem'}}>Offline Ready</span> 
                            : <button className="btn" style={{padding:'5px 10px'}} onClick={() => handleDownload(file.id, file.name)}>Download</button>
                        }
                    </div>
                </div>
            ))}
        </div>
    </div>
  );
}