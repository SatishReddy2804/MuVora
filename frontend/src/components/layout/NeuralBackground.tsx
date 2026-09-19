import React from 'react';

export const NeuralBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none z-[-1] overflow-hidden">
      {/* Background Gradient Mesh */}
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-brand-violet/10 blur-[130px]" />
      <div className="absolute top-[20%] right-[-10%] w-[45vw] h-[45vw] rounded-full bg-brand-cyan/10 blur-[140px]" />
      <div className="absolute bottom-[-10%] left-[20%] w-[55vw] h-[40vw] rounded-full bg-brand-blue/10 blur-[150px]" />

      {/* Cyber Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.03]" 
        style={{
          backgroundImage: `radial-gradient(rgba(255, 255, 255, 0.4) 1px, transparent 1px)`,
          backgroundSize: '32px 32px'
        }}
      />
    </div>
  );
};
