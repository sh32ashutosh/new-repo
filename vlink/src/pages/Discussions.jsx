import { useState, useEffect } from 'react';
import { getDashboardData } from '../services/api'; // In real app: getDiscussions()
import Modal from '../components/common/Modal';
import { toast } from 'react-toastify';
import { FaThumbsUp, FaReply, FaPlus } from 'react-icons/fa';

export default function Discussions() {
  const [discussions, setDiscussions] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Form State
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');

  useEffect(() => {
    getDashboardData().then(data => setDiscussions(data.discussions));
  }, []);

  const handlePost = (e) => {
    e.preventDefault();
    const newPost = {
      id: Date.now(),
      title: newTitle,
      content: newContent,
      author: "You",
      replies: 0
    };
    setDiscussions([newPost, ...discussions]);
    setIsModalOpen(false);
    setNewTitle('');
    setNewContent('');
    toast.success("Discussion Posted!");
    // In real app: call api.postDiscussion(newPost)
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Discussion Board</h2>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <FaPlus style={{ marginRight: '8px' }} /> New Discussion
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {discussions.map(d => (
          <div key={d.id} className="card">
            <h3>{d.title}</h3>
            <p style={{ color: '#ccc', margin: '10px 0' }}>{d.content}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: '#888', fontSize: '0.9rem' }}>
              <span>{d.author}</span>
              <div style={{ display: 'flex', gap: '15px' }}>
                <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}><FaThumbsUp /> Like</span>
                <span style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}><FaReply /> {d.replies} Replies</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* New Discussion Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Start New Discussion">
        <form onSubmit={handlePost}>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Title</label>
            <input className="input-field" required value={newTitle} onChange={e => setNewTitle(e.target.value)} />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Content</label>
            <textarea 
              className="input-field" 
              rows="4" 
              required 
              value={newContent} 
              onChange={e => setNewContent(e.target.value)}
              style={{ resize: 'vertical' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Post</button>
        </form>
      </Modal>
    </div>
  );
}
