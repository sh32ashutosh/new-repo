import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getDashboardData } from '../services/api';
import { createClass, joinClass } from '../services/classroomService';
import { toast } from 'react-toastify';
import Modal from '../components/common/Modal';
import { FaPlus, FaVideo, FaChalkboardTeacher, FaUserFriends } from 'react-icons/fa';

export default function Classes() {
  const { user } = useAuth();
  const navigate = useNavigate();
  // Initialize with empty array
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newClassTitle, setNewClassTitle] = useState('');
  const [joinCode, setJoinCode] = useState('');

  const isTeacher = user?.role === 'teacher';

  useEffect(() => {
    getDashboardData()
      .then(data => {
        // ⚡ SAFETY CHECK: Ensure data.classes exists
        if (data && data.classes) {
            setClasses(data.classes);
        } else {
            setClasses([]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load classes:", err);
        setClasses([]); // Fallback to empty
        setLoading(false);
      });
  }, []);

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      const newClass = await createClass(newClassTitle);
      // Optimistically add to list
      setClasses(prev => [...prev, newClass]);
      setIsModalOpen(false);
      setNewClassTitle('');
      toast.success(`Class "${newClass.title}" Created! Code: ${newClass.code}`);
    } catch (error) {
      toast.error('Failed to create class');
    }
  };

  const handleJoinClass = async (e) => {
    e.preventDefault();
    try {
      const res = await joinClass(joinCode);
      if (res.success) {
        toast.success('Joined class successfully!');
        // Ideally we'd fetch the class details and add it to the list here,
        // but navigating to it is a good immediate feedback.
        navigate(`/classroom/${res.classId}`);
      }
    } catch (error) {
      toast.error(error.message || 'Invalid Class Code');
    }
  };

  if (loading) return <div style={{padding: '20px'}}>Loading Classes...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>My Classes</h2>
        
        {isTeacher ? (
          <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
            <FaPlus style={{ marginRight: '8px' }} /> Create Class
          </button>
        ) : (
          <form onSubmit={handleJoinClass} style={{ display: 'flex', gap: '10px' }}>
            <input 
              className="input-field" 
              placeholder="Enter Class Code" 
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              style={{ marginBottom: 0, width: '200px' }}
            />
            <button type="submit" className="btn btn-success">Join</button>
          </form>
        )}
      </div>

      {classes.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#888', marginTop: '50px' }}>
            <p>You haven't joined any classes yet.</p>
            {!isTeacher && <p>Ask your teacher for a code!</p>}
        </div>
      ) : (
        <div className="dashboard-grid">
            {classes.map((cls) => (
            <div key={cls.id} className={`card ${cls.status === 'live' ? 'live-active' : ''}`} style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ margin: 0, fontSize: '1.2rem' }}>{cls.title}</h3>
                    {cls.status === 'live' && (
                    <span style={{ background: '#16a34a', color: 'white', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <span className="live-badge" style={{ width: '6px', height: '6px' }}></span> LIVE
                    </span>
                    )}
                </div>
                <p style={{ color: '#888', fontSize: '0.9rem', marginTop: '5px' }}>{cls.teacher}</p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', color: '#ccc' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><FaUserFriends /> {cls.participants || 0} Students</span>
                {isTeacher && <span style={{ fontFamily: 'monospace', background: '#333', padding: '2px 6px', borderRadius: '4px' }}>Code: {cls.code}</span>}
                </div>

                <button 
                className={`btn ${cls.status === 'live' ? 'btn-success' : 'btn-primary'}`} 
                style={{ width: '100%', marginTop: 'auto' }}
                onClick={() => navigate(`/classroom/${cls.id}`)}
                >
                {cls.status === 'live' ? (
                    <><FaVideo style={{ marginRight: '8px' }} /> Join Live Class</>
                ) : (
                    <><FaChalkboardTeacher style={{ marginRight: '8px' }} /> View Classroom</>
                )}
                </button>
            </div>
            ))}
        </div>
      )}

      {/* Create Class Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Class">
        <form onSubmit={handleCreateClass}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', color: '#ccc' }}>Class Name / Title</label>
            <input 
              className="input-field" 
              placeholder="e.g., Physics 101" 
              value={newClassTitle} 
              onChange={(e) => setNewClassTitle(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Create & Generate Code</button>
        </form>
      </Modal>
    </div>
  );
}