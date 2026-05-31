/* Settings panel — mirrors Gradio's caption settings controls */

import React from 'react';

interface SettingsPanelProps {
  settings: {
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
  onChange: (settings: Partial<SettingsPanelProps['settings']>) => void;
}

const TRANSCRIPTION_ENGINES = [
  'Whisper Large v3 (Recommended Quality)',
  'Whisper Large v3 Turbo (Fastest)',
  'Whisper Medium (Lighter)',
  'Whisper Small (Lightest)',
  'Whisper Base (Smallest)',
  'Apex Hinglish (Legacy)',
];

const SettingsPanel: React.FC<SettingsPanelProps> = ({ settings, onChange }) => {
  return (
    <div className="pyko-glass-panel pyko-fade-in">
      <span className="caps-label">Caption Settings</span>

      {/* Word-level toggle */}
      <div className="pyko-checkbox-label" style={{ marginBottom: '1rem' }}>
        <input
          type="checkbox"
          id="word_level"
          checked={settings.word_level}
          onChange={(e) => onChange({ word_level: e.target.checked })}
        />
        <label htmlFor="word_level">Word-level alignment (per-word timings)</label>
      </div>

      {/* Transcription engine */}
      <div style={{ marginBottom: '1rem' }}>
        <label className="pyko-label" htmlFor="transcription_engine">Engine</label>
        <select
          id="transcription_engine"
          className="pyko-select"
          value={settings.transcription_engine}
          onChange={(e) => onChange({ transcription_engine: e.target.value })}
        >
          {TRANSCRIPTION_ENGINES.map((eng) => (
            <option key={eng} value={eng}>{eng}</option>
          ))}
        </select>
      </div>

      {/* Grid settings */}
      <div className="pyko-settings-row" style={{ marginBottom: '1rem' }}>
        <div>
          <label className="pyko-label" htmlFor="lines">Lines</label>
          <select
            id="lines"
            className="pyko-select"
            value={settings.lines}
            onChange={(e) => onChange({ lines: e.target.value })}
          >
            <option value="Single">Single</option>
            <option value="Double">Double</option>
          </select>
        </div>
        <div>
          <label className="pyko-label" htmlFor="max_chars">Max chars / line</label>
          <input
            id="max_chars"
            className="pyko-input"
            type="number"
            min={1}
            max={99}
            value={settings.max_chars}
            onChange={(e) => onChange({ max_chars: parseInt(e.target.value) || 42 })}
          />
        </div>
        <div>
          <label className="pyko-label" htmlFor="min_duration">Min duration (s)</label>
          <input
            id="min_duration"
            className="pyko-input"
            type="number"
            min={0.3}
            max={10}
            step={0.1}
            value={settings.min_duration}
            onChange={(e) => onChange({ min_duration: parseFloat(e.target.value) || 3.0 })}
          />
        </div>
      </div>

      <div className="pyko-settings-row" style={{ marginBottom: '1rem' }}>
        <div>
          <label className="pyko-label" htmlFor="gap_frames">Gap frames</label>
          <input
            id="gap_frames"
            className="pyko-input"
            type="number"
            min={0}
            max={10}
            value={settings.gap_frames}
            onChange={(e) => onChange({ gap_frames: parseInt(e.target.value) || 0 })}
          />
        </div>
        <div>
          <label className="pyko-label" htmlFor="offset_seconds">Timing offset (s)</label>
          <input
            id="offset_seconds"
            className="pyko-input"
            type="number"
            min={-5}
            max={5}
            step={0.05}
            value={settings.offset_seconds}
            onChange={(e) => onChange({ offset_seconds: parseFloat(e.target.value) || 0 })}
          />
        </div>
      </div>

      {/* Custom replacements */}
      <div className="pyko-checkbox-label">
        <input
          type="checkbox"
          id="enable_custom_replacements"
          checked={settings.enable_custom_replacements}
          onChange={(e) => onChange({ enable_custom_replacements: e.target.checked })}
        />
        <label htmlFor="enable_custom_replacements">Enable custom replacements</label>
      </div>

      {settings.enable_custom_replacements && (
        <div style={{ marginTop: '1rem' }}>
          <label className="pyko-label" htmlFor="custom_replacements_file">
            Custom dictionary JSON path
          </label>
          <input
            id="custom_replacements_file"
            className="pyko-input"
            type="text"
            placeholder="C:\\path\\to\\replacements.json"
            value={settings.custom_replacements_file}
            onChange={(e) => onChange({ custom_replacements_file: e.target.value })}
          />
        </div>
      )}
    </div>
  );
};

export default SettingsPanel;
