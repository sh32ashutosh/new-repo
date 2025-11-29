import React from 'react';
import '../../styles/App.css'; // Ensure global styles are loaded

export default function Button({ children, variant = 'primary', onClick, style, className = '', ...props }) {
  // variants: primary, success, danger, warning, outline
  const btnClass = `btn btn-${variant} ${className}`;
  
  return (
    <button className={btnClass} onClick={onClick} style={style} {...props}>
      {children}
    </button>
  );
}