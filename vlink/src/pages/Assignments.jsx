import { useState, useEffect } from 'react';
import Modal from '../components/common/Modal';
import { toast } from 'react-toastify';

export default function Assignments() {
  const [assignments, setAssignments] = useState([]);
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' or 'completed'
  const [isQuizOpen, setIsQuizOpen] = useState(false);
  const [currentQuiz, setCurrentQuiz] = useState(null);
  const [loading, setLoading] = useState(true);

  // Form State for Quiz
  const [selectedAnswer, setSelectedAnswer] = useState(null);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const res = await fetch('http://localhost:8000/api/assignments/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            setAssignments(data || []);
        }
    } catch (err) {
        console.error(err);
    } finally {
        setLoading(false);
    }
  };

  // Safe filtering
  const pending = assignments.filter(a => a.status === 'pending');
  const completed = assignments.filter(a => a.status === 'completed');

  const handleTakeQuiz = (assignment) => {
    setCurrentQuiz(assignment);
    setSelectedAnswer(null); // Reset answer
    setIsQuizOpen(true);
  };

  const submitQuiz = async () => {
    if (!selectedAnswer) {
        toast.warning("Please select an answer!");
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        const res = await fetch(`http://localhost:8000/api/assignments/${currentQuiz.id}/submit`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ 
                answers: { q1: selectedAnswer } 
            })
        });

        const data = await res.json();

        if (data.success) {
            setIsQuizOpen(false);
            toast.success(data.message || "Quiz Submitted!");
            // Refresh list to move item to completed tab
            fetchAssignments();
        } else {
            toast.error(data.message || "Submission failed");
        }
    } catch (error) {
        toast.error("Server Error");
    }
  };

  if (loading) return <div style={{padding:'20px'}}>Loading Assignments...</div>;

  return (
    <div>
      <div className="grid-4">
        <div className="card stat-card"><div><p style={{color:'#888'}}>Pending</p><p className="stat-value">{pending.length}</p></div><div style={{color: '#ea580c', fontSize: '1.5rem'}}>!</div></div>
        <div className="card stat-card"><div><p style={{color:'#888'}}>Completed</p><p className="stat-value">{completed.length}</p></div><div style={{color: '#16a34a', fontSize: '1.5rem'}}>✓</div></div>
        <div className="card stat-card"><div><p style={{color:'#888'}}>Avg Score</p><p className="stat-value">85%</p></div><div style={{color: '#ca8a04', fontSize: '1.5rem'}}>★</div></div>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <button className={`btn ${activeTab === 'pending' ? 'btn-primary' : ''}`} style={{ marginRight: '10px' }} onClick={() => setActiveTab('pending')}>Pending</button>
        <button className={`btn ${activeTab === 'completed' ? 'btn-primary' : ''}`} onClick={() => setActiveTab('completed')}>Completed</button>
      </div>

      <div className="card">
        {(activeTab === 'pending' ? pending : completed).length === 0 ? (
             <p style={{ padding: '20px', color: '#666' }}>No {activeTab} assignments found.</p>
        ) : (
            (activeTab === 'pending' ? pending : completed).map(a => (
            <div key={a.id} style={{ padding: '20px', borderBottom: '1px solid #333', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                <h3>{a.title}</h3>
                <p style={{ color: '#888' }}>{a.details}</p>
                </div>
                {activeTab === 'pending' ? (
                <button className="btn btn-warning" onClick={() => handleTakeQuiz(a)}>Take Quiz</button>
                ) : (
                <span style={{ color: '#16a34a', fontWeight: 'bold' }}>{a.score}/{a.total}</span>
                )}
            </div>
            ))
        )}
      </div>

      {/* Quiz Modal */}
      <Modal isOpen={isQuizOpen} onClose={() => setIsQuizOpen(false)} title={`Quiz: ${currentQuiz?.title}`}>
        <div style={{ marginBottom: '20px' }}>
          <p><strong>1. What is the value of Pi?</strong></p>
          <div style={{ display: 'flex', gap: '15px', marginTop: '10px' }}>
            <label>
                <input 
                    type="radio" 
                    name="q1" 
                    value="3.14" 
                    onChange={(e) => setSelectedAnswer(e.target.value)} 
                /> 3.14
            </label>
            <label>
                <input 
                    type="radio" 
                    name="q1" 
                    value="2.14" 
                    onChange={(e) => setSelectedAnswer(e.target.value)} 
                /> 2.14
            </label>
          </div>
        </div>
        <button className="btn btn-success" style={{ width: '100%' }} onClick={submitQuiz}>Submit Quiz</button>
      </Modal>
    </div>
  );
}