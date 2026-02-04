// src/components/ChartCard.tsx
import React from 'react';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

const ChartCard: React.FC<ChartCardProps> = ({ title, children }) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 flex flex-col">
      <h2 className="text-lg font-bold mb-4">{title}</h2>
      <div className="flex-1">{children}</div>
    </div>
  );
};

export default ChartCard;
