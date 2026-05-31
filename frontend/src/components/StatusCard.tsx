/* Status card — renders HTML from the backend status response */

import React from 'react';

interface StatusCardProps {
  html: string | null;
}

const StatusCard: React.FC<StatusCardProps> = ({ html }) => {
  if (!html) return null;

  return (
    <div
      className="pyko-fade-in"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};

export default StatusCard;
