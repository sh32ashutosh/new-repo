import React from 'react';
import { Line } from 'react-konva';

export default function VectorLayer({ lines }) {
  if (!lines) return null;

  return (
    <>
      {lines.map((line, i) => (
        <Line
          key={i}
          points={line.points}
          stroke={line.tool === 'eraser' ? '#ffffff' : '#df4b26'} // Default red color, eraser is white
          strokeWidth={line.tool === 'eraser' ? 20 : 5}
          tension={0.5}
          lineCap="round"
          lineJoin="round"
          globalCompositeOperation={
            line.tool === 'eraser' ? 'destination-out' : 'source-over'
          }
        />
      ))}
    </>
  );
}