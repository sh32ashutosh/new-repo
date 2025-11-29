import React, { useRef } from 'react';
import { Stage, Layer } from 'react-konva';
import VectorLayer from './VectorLayer';

// Accept 'lines' as a prop
export default function Whiteboard({ width, height, tool, isTeacher, onDrawEnd, lines }) {
  const isDrawing = useRef(false);

  const handleMouseDown = (e) => {
    // Only teachers can initiate drawing
    if (!isTeacher) return;
    
    isDrawing.current = true;
    const stage = e.target.getStage();
    const pos = stage.getPointerPosition();
    onDrawEnd('start', { x: pos.x, y: pos.y, tool });
  };

  const handleMouseMove = (e) => {
    // Only teachers can draw
    if (!isTeacher || !isDrawing.current) return;
    
    const stage = e.target.getStage();
    const point = stage.getPointerPosition();
    onDrawEnd('move', { x: point.x, y: point.y });
  };

  const handleMouseUp = () => {
    isDrawing.current = false;
    onDrawEnd('end', {});
  };

  // Mobile/Touch Support handlers
  const handleTouchStart = (e) => {
    if (!isTeacher) return;
    // prevent scrolling when drawing
    // e.evt.preventDefault(); 
    handleMouseDown(e);
  };

  return (
    <div 
      className="whiteboard-wrapper" 
      style={{ 
        width: '100%', 
        height: '100%', 
        cursor: isTeacher ? `crosshair` : 'default', // Visual cue for teacher
        touchAction: 'none' // Important for touch devices
      }}
    >
      <Stage
        width={width}
        height={height}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleMouseMove}
        onTouchEnd={handleMouseUp}
      >
        {/* FIX: VectorLayer must be INSIDE the <Layer> component */}
        <Layer>
            {/* Background Image Logic would go here */}
            
            {/* Pass lines to VectorLayer */}
            <VectorLayer lines={lines} /> 
        </Layer>
      </Stage>
    </div>
  );
}