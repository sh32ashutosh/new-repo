import React from 'react';
import { FaPen, FaEraser, FaTrash, FaImage } from 'react-icons/fa';

export default function ToolsPanel({ setTool, clearCanvas }) {
  return (
    <div className="tools-panel">
      <h4>Tools</h4>
      <div className="tool-grid">
        <button className="btn-tool" onClick={() => setTool('pen')} title="Pen"><FaPen /></button>
        <button className="btn-tool" onClick={() => setTool('eraser')} title="Eraser"><FaEraser /></button>
        <button className="btn-tool" onClick={clearCanvas} title="Clear Board"><FaTrash /></button>
        <button className="btn-tool" title="Upload Slide"><FaImage /></button>
      </div>
      
      <h4>Colors</h4>
      <div className="color-picker">
        <div className="color-dot" style={{background: '#df4b26'}} onClick={() => {}} />
        <div className="color-dot" style={{background: '#2563eb'}} onClick={() => {}} />
        <div className="color-dot" style={{background: '#ffffff'}} onClick={() => {}} />
      </div>
    </div>
  );
}