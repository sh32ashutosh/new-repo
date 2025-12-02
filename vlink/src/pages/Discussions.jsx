import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // Added useNavigate
import Modal from '../components/common/Modal';
import { toast } from 'react-toastify';
import { FaThumbsUp, FaReply, FaPlus } from 'react-icons/fa';

export default function Discussions() {
  const [discussions, setDiscussions] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const { id } = useParams();
  const navigate = useNavigate(); // For redirecting to login
  const activeClassId = id || "physics-101"; 

  const [newContent, setNewContent] = useState('');

  useEffect(() => {
    fetchDiscussions();
  }, [activeClassId]);

  const fetchDiscussions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      // If no token, force login immediately
      if (!token) {
        navigate('/login');
        return;
      }

      const res = await fetch(`http://localhost:8000/api/discussions/class/${activeClassId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      // ⚡ AUTO-LOGOUT FIX
      if (res.status === 401) {
        toast.error("Session expired. Please login again.");
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        navigate('/login');
        return;
      }
      
      if (res.ok) {
        const data = await res.json();
        setDiscussions(data);
      }
    } catch (err) {
      console.error("Failed to load chat", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/discussions/class/${activeClassId}`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: newContent })
      });

      // ⚡ AUTO-LOGOUT FIX
      if (res.status === 401) {
        navigate('/login');
        return;
      }

      if (res.ok) {
        const data = await res.json();
        setDiscussions([...discussions, data.post]);
        setIsModalOpen(false);
        setNewContent('');
        toast.success("Message Posted!");
      } else {
        toast.error("Failed to post message");
      }
    } catch (error) {
      toast.error("Server Error");
    }
  };

  if (loading) return <div style={{padding:'20px'}}>Loading Chat...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Classroom Chat</h2>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <FaPlus style={{ marginRight: '8px' }} /> New Message
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {discussions.length === 0 ? <p style={{color:'#666'}}>No messages yet. Be the first!</p> : null}

        {discussions.map(d => (
          <div key={d.id} className="card" style={{ 
              borderLeft: d.is_me ? '4px solid #2563eb' : '4px solid #333',
              background: d.is_me ? '#1e293b' : '#111' 
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 'bold', color: d.is_me ? '#60a5fa' : '#fff' }}>
                    {d.user} {d.is_me && "(You)"}
                </span>
                <span style={{ color: '#666', fontSize: '0.8rem' }}>{d.time}</span>
            </div>
            
            <p style={{ color: '#e2e8f0', margin: '10px 0', whiteSpace: 'pre-wrap' }}>{d.text}</p>
            
            <div style={{ display: 'flex', gap: '15px', color: '#64748b', fontSize: '0.9rem' }}>
              <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}><FaThumbsUp /> Like</span>
            </div>
          </div>
        ))}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="New Message">
        <form onSubmit={handlePost}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Message</label>
            <textarea 
              className="input-field" 
              rows="4" 
              required 
              value={newContent} 
              onChange={e => setNewContent(e.target.value)}
              style={{ resize: 'vertical' }}
              placeholder="Type your question or announcement..."
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Post</button>
        </form>
      </Modal>
    </div>
  );
}