/* Batch processing tab — multi-video upload with background job polling */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import FileDropzone from './FileDropzone';
import SettingsPanel from './SettingsPanel';
import StatusCard from './StatusCard';
import {
  startBatchJob,
  getJobStatus,
  getDownloadUrl,
  deleteJob,
} from '../api';

interface BatchProcessingTabProps {
  currentPreset: string;
  presetSettings: {
    word_level: boolean;
    transcription_engine: string;
    enable_custom_replacements: boolean;
    custom_replacements_file: string;
    format_name: string;
    stream: string;
    style: string;
    max_chars: number;
    min_duration: number;
    gap_frames: number;
    lines: string;
    offset_seconds: number;
  };
  onPresetChange: (name: string, settings: any) => void;
}

const BatchProcessingTab: React.FC<BatchProcessingTabProps> = ({
  currentPreset,
  presetSettings,
  onPresetChange,
}) => {
  const [videos, setVideos] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusHtml, setStatusHtml] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval>>();

  const handleFilesSelected = useCallback((files: File[]) => {
    setVideos((prev) => [...prev, ...files]);
    setStatusHtml(null);
  }, []);

  const removeFile = useCallback((index: number) => {
    setVideos((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSettingsChange = useCallback((partial: Partial<typeof presetSettings>) => {
    onPresetChange('custom', { ...presetSettings, ...partial });
  }, [presetSettings, onPresetChange]);

  const handleStart = useCallback(async () => {
    if (videos.length === 0) return;

    setLoading(true);
    setStatusHtml(null);
    setJobId(null);

    try {
      const params: Record<string, string | boolean | number> = {
        word_level: presetSettings.word_level,
        transcription_engine: presetSettings.transcription_engine,
        enable_custom_replacements: presetSettings.enable_custom_replacements,
        custom_replacements_file: presetSettings.custom_replacements_file,
        caption_preset: currentPreset,
        format_name: presetSettings.format_name,
        stream: presetSettings.stream,
        style: presetSettings.style,
        max_chars: presetSettings.max_chars,
        min_duration: presetSettings.min_duration,
        gap_frames: presetSettings.gap_frames,
        lines: presetSettings.lines,
        offset_seconds: presetSettings.offset_seconds,
      };

      const { job_id } = await startBatchJob(videos, params);
      setJobId(job_id);

      // Start polling
      const interval = setInterval(async () => {
        try {
          const status = await getJobStatus(job_id);
          if (status.status === 'done' || status.status === 'error') {
            clearInterval(interval);
            setLoading(false);
            setJobId(status.status === 'done' ? job_id : null);
            setStatusHtml(status.status_html);
          }
        } catch {
          clearInterval(interval);
          setLoading(false);
        }
      }, 2000);

      pollRef.current = interval;
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Batch start failed';
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-error"><div class="status-label">Status</div><div class="status-title">Error</div><div class="status-message">${msg}</div></div></div>`
      );
      setLoading(false);
    }
  }, [videos, presetSettings, currentPreset]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const handleDownload = useCallback(() => {
    if (!jobId) return;
    const filename = 'hinglishcaps_batch.zip';
    const link = document.createElement('a');
    link.href = getDownloadUrl(jobId, filename);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }, [jobId]);

  const handleReset = useCallback(() => {
    if (jobId) deleteJob(jobId).catch(() => {});
    setVideos([]);
    setStatusHtml(null);
    setJobId(null);
    setLoading(false);
    if (pollRef.current) clearInterval(pollRef.current);
  }, [jobId]);

  return (
    <div>
      <div className="pyko-row">
        <div className="pyko-col">
          {/* Upload */}
          <div className="pyko-glass-panel">
            <span className="caps-label">Upload Videos ({videos.length})</span>
            <FileDropzone
              multiple
              onFilesSelected={handleFilesSelected}
              label="Drop video files here for batch processing"
            />
            {videos.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                {videos.map((f, i) => (
                  <div key={i} className="pyko-file-preview">
                    <span className="file-name">{f.name}</span>
                    <button className="file-remove" onClick={() => removeFile(i)}>
                      &times;
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Settings */}
          <SettingsPanel settings={presetSettings} onChange={handleSettingsChange} />
        </div>

        <div className="pyko-col">
          {/* Controls */}
          <div className="pyko-glass-panel">
            <span className="caps-label">Batch Controls</span>
            <p style={{ color: 'var(--pyko-text-muted)', fontSize: '0.875rem' }}>
              Preset: <strong>{currentPreset}</strong>
            </p>
            <div className="pyko-flex-between">
              <button
                className="pyko-solid-button"
                disabled={videos.length === 0 || loading}
                onClick={handleStart}
              >
                {loading ? 'Processing...' : `Process ${videos.length} video(s)`}
              </button>
              <button
                className="pyko-outline-button"
                onClick={handleReset}
              >
                Clear
              </button>
            </div>
            {loading && (
              <div className="pyko-flex-center" style={{ marginTop: '1rem' }}>
                <div className="pyko-spinner" />
                <span style={{ color: 'var(--pyko-text-muted)', fontSize: '0.875rem' }}>
                  Processing batch...
                </span>
              </div>
            )}
          </div>

          {/* Status */}
          <StatusCard html={statusHtml} />

          {/* Download */}
          {jobId && !loading && (
            <div className="pyko-result-row pyko-fade-in">
              <span className="caps-label">Download Results</span>
              <button className="pyko-outline-button" onClick={handleDownload}>
                Download ZIP
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BatchProcessingTab;
