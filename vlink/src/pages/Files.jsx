import { useState, useEffect } from 'react';
import { getDashboardData, uploadFileMock } from '../services/api';
import { toast } from 'react-toastify';

export default function Files() {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    getDashboardData().then(data => setFiles(data.files));
  }, []);

  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Simulate Tus.io upload
    uploadFileMock(file, (progress) => {
      setUploadProgress(progress);
    }).then(() => {
        toast.success("File Uploaded Successfully!");
        setUploadProgress(0);
        setFiles([...files, { id: Date.now(), name: file.name, size: '2 MB', offline: false }]);
    });
  };

  return (
    <div>
        <div style={{display:'flex', justifyContent:'space-between', marginBottom:'20px'}}>
            <h2>Class Resources</h2>
            <div style={{position:'relative'}}>
                <input type="file" onChange={handleUpload} style={{position:'absolute', opacity:0, width:'100%', height:'100%', cursor:'pointer'}} />
                <button className="btn btn-primary">Upload File (Tus.io)</button>
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
                            : <button className="btn" style={{padding:'5px 10px'}}>Download</button>
                        }
                    </div>
                </div>
            ))}
        </div>
    </div>
  );
}