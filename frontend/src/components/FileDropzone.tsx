/* File dropzone — single or multi file upload */

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileDropzoneProps {
  multiple?: boolean;
  accept?: Record<string, string[]>;
  onFilesSelected: (files: File[]) => void;
  label?: string;
}

const VIDEO_ACCEPT: Record<string, string[]> = {
  'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'],
};

const FileDropzone: React.FC<FileDropzoneProps> = ({
  multiple = false,
  accept = VIDEO_ACCEPT,
  onFilesSelected,
  label,
}) => {
  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      onFilesSelected(accepted);
    }
  }, [onFilesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
    maxSize: 2 * 1024 * 1024 * 1024, // 2GB
  });

  return (
    <div
      {...getRootProps()}
      className={`pyko-dropzone ${isDragActive ? 'active' : ''}`}
    >
      <input {...getInputProps()} />
      <div className="drop-icon">{isDragActive ? '📂' : '🎬'}</div>
      {label && <p>{label}</p>}
      {!label && (
        <p>
          {isDragActive
            ? 'Drop your video here...'
            : multiple
              ? 'Drag & drop video files here, or click to browse'
              : 'Drag & drop a video file here, or click to browse'}
        </p>
      )}
    </div>
  );
};

export default FileDropzone;
