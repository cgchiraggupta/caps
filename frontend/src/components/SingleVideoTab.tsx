/* Single video caption generation tab */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import FileDropzone from './FileDropzone';
import SettingsPanel from './SettingsPanel';
import StatusCard from './StatusCard';
import {
  deleteJob,
  getDownloadUrl,
  getJobStatus,
  startSingleJob,
} from '../api';

interface SingleVideoTabProps {
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

const SingleVideoTab: React.FC<SingleVideoTabProps> = ({
  currentPreset,
  presetSettings,
  onPresetChange,
}) => {
  const [video, setVideo] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusHtml, setStatusHtml] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [resultFilename, setResultFilename] = useState('');
  const pollRef = useRef<ReturnType<typeof setInterval>>();

  const clearPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = undefined;
    }
  }, []);

  const handleFilesSelected = useCallback((files: File[]) => {
    if (files.length > 0) {
      setVideo(files[0]);
      setJobId(null);
      setResultFilename('');
      setStatusHtml(null);
      clearPolling();
    }
  }, [clearPolling]);

  const handleSettingsChange = useCallback((partial: Partial<typeof presetSettings>) => {
    onPresetChange('custom', { ...presetSettings, ...partial });
  }, [presetSettings, onPresetChange]);

  const handleGenerate = useCallback(async () => {
    if (!video) return;

    setLoading(true);
    setStatusHtml(
      '<div class="status-shell"><div class="status-card status-ready"><div class="status-label">Status</div><div class="status-title">Queued</div><div class="status-message">Caption generation has started. You can leave this tab open while the model works.</div></div></div>'
    );
    if (jobId) deleteJob(jobId).catch(() => {});
    setJobId(null);
    setResultFilename('');
    clearPolling();

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

      const { job_id } = await startSingleJob(video, params);
      setJobId(job_id);

      const interval = setInterval(async () => {
        try {
          const status = await getJobStatus(job_id);
          if (status.status === 'done' || status.status === 'error') {
            clearInterval(interval);
            pollRef.current = undefined;
            setLoading(false);
            setStatusHtml(status.status_html);

            if (status.status === 'done') {
              setJobId(job_id);
              setResultFilename(status.result_filename || 'captions.srt');
            } else {
              setJobId(null);
              setResultFilename('');
            }
          }
        } catch (err: any) {
          clearInterval(interval);
          pollRef.current = undefined;
          setLoading(false);
          const msg = err?.response?.data?.detail || err?.message || 'Could not read job status';
          setStatusHtml(
            `<div class="status-shell"><div class="status-card status-error"><div class="status-label">Status</div><div class="status-title">Error</div><div class="status-message">${msg}</div></div></div>`
          );
        }
      }, 2000);

      pollRef.current = interval;
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Generation start failed';
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-error"><div class="status-label">Status</div><div class="status-title">Error</div><div class="status-message">${msg}</div></div></div>`
      );
      setJobId(null);
      setLoading(false);
    }
  }, [video, presetSettings, currentPreset, jobId, clearPolling]);

  useEffect(() => {
    return () => clearPolling();
  }, [clearPolling]);

  const handleDownload = useCallback(() => {
    if (!jobId) return;
    const filename = resultFilename || 'captions.srt';
    const link = document.createElement('a');
    link.href = getDownloadUrl(jobId, filename);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }, [jobId, resultFilename]);

  const handleClear = useCallback(() => {
    if (jobId) deleteJob(jobId).catch(() => {});
    clearPolling();
    setVideo(null);
    setStatusHtml(null);
    setJobId(null);
    setResultFilename('');
    setLoading(false);
  }, [jobId, clearPolling]);

  return (
    <div>
      <div className="pyko-row">
        <div className="pyko-col">
          <div className="pyko-glass-panel">
            <span className="caps-label">Upload Video</span>
            <FileDropzone
              onFilesSelected={handleFilesSelected}
              label={video ? `Selected: ${video.name}` : 'Drop a video file here'}
            />
          </div>

          <SettingsPanel settings={presetSettings} onChange={handleSettingsChange} />
        </div>

        <div className="pyko-col">
          <div className="pyko-glass-panel">
            <span className="caps-label">Generate</span>
            <p style={{ color: 'var(--pyko-text-muted)', fontSize: '0.875rem' }}>
              Preset: <strong>{currentPreset}</strong>
            </p>
            <div className="pyko-flex-between">
              <button
                className="pyko-solid-button"
                disabled={!video || loading}
                onClick={handleGenerate}
              >
                {loading ? 'Generating...' : 'Generate Captions'}
              </button>
              <button
                className="pyko-outline-button"
                disabled={loading}
                onClick={handleClear}
              >
                Clear
              </button>
            </div>
            {loading && (
              <div className="pyko-flex-center" style={{ marginTop: '1rem' }}>
                <div className="pyko-spinner" />
                <span style={{ color: 'var(--pyko-text-muted)', fontSize: '0.875rem' }}>
                  Model is transcribing in the background...
                </span>
              </div>
            )}
          </div>

          <StatusCard html={statusHtml} />

          {jobId && !loading && (
            <div className="pyko-result-row pyko-fade-in">
              <span className="caps-label">Download</span>
              <button className="pyko-outline-button" onClick={handleDownload}>
                Download {resultFilename || 'captions.srt'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SingleVideoTab;
