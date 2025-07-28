import React from 'react';

interface ModernCardProps {
  children: React.ReactNode;
  className?: string;
}

const ModernCard: React.FC<ModernCardProps> = ({ children, className }) => {
  return (
    <div className={`bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6 transition-all duration-300 hover:shadow-xl ${className}`}>
      {children}
    </div>
  );
};

export default ModernCard;
