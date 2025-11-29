import React from 'react';

export default function Input({ label, type = 'text', value, onChange, placeholder, required = false }) {
  return (
    <div style={{ marginBottom: '15px' }}>
      {label && <label style={{ display: 'block', marginBottom: '8px', color: '#ccc' }}>{label}</label>}
      <input 
        className="input-field" 
        type={type} 
        value={value} 
        onChange={onChange} 
        placeholder={placeholder} 
        required={required}
      />
    </div>
  );
}