/* Preset manager — list, save, delete, and select presets */

import React, { useState, useEffect, useCallback } from 'react';
import StatusCard from './StatusCard';
import {
  Preset,
  getPresets,
  savePreset as apiSavePreset,
  deletePreset as apiDeletePreset,
} from '../api';

interface PresetManagerProps {
  presets: Preset[];
  currentPreset: string;
  onPresetChange: (name: string, settings: any) => void;
  onPresetsUpdated: (presets: Preset[]) => void;
}

const PresetManager: React.FC<PresetManagerProps> = ({
  presets,
  currentPreset,
  onPresetChange,
  onPresetsUpdated,
}) => {
  const [newName, setNewName] = useState('');
  const [statusHtml, setStatusHtml] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPresets()
      .then((data) => {
        onPresetsUpdated(data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = useCallback((preset: Preset) => {
    const settings = {
      word_level: false,
      transcription_engine: 'Whisper Large v3 (Recommended Quality)',
      enable_custom_replacements: false,
      custom_replacements_file: '',
      format_name: preset.format_name,
      stream: preset.stream,
      style: preset.style,
      max_chars: preset.max_chars,
      min_duration: preset.min_duration,
      gap_frames: preset.gap_frames,
      lines: preset.lines,
      offset_seconds: -0.18,
    };
    onPresetChange(preset.name, settings);
    setStatusHtml(
      `<div class="status-shell"><div class="status-card status-ready"><div class="status-label">Status</div><div class="status-title">Selected</div><div class="status-message">Preset "${preset.name}" is now active.</div></div></div>`
    );
  }, [onPresetChange]);

  const handleSave = useCallback(async () => {
    if (!newName.trim()) return;

    // Find the current preset settings
    const current = presets.find((p) => p.name === currentPreset);
    if (!current) return;

    try {
      await apiSavePreset({ ...current, name: newName.trim() });
      const updated = await getPresets();
      onPresetsUpdated(updated);
      setNewName('');
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-success"><div class="status-label">Status</div><div class="status-title">Saved</div><div class="status-message">Preset "${newName.trim()}" saved.</div></div></div>`
      );
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Save failed';
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-error"><div class="status-label">Status</div><div class="status-title">Error</div><div class="status-message">${msg}</div></div></div>`
      );
    }
  }, [newName, currentPreset, presets, onPresetsUpdated]);

  const handleDelete = useCallback(async (name: string) => {
    if (!window.confirm(`Delete preset "${name}"?`)) return;

    try {
      await apiDeletePreset(name);
      const updated = await getPresets();
      onPresetsUpdated(updated);
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-warning"><div class="status-label">Status</div><div class="status-title">Deleted</div><div class="status-message">Preset "${name}" deleted.</div></div></div>`
      );
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Delete failed';
      setStatusHtml(
        `<div class="status-shell"><div class="status-card status-error"><div class="status-label">Status</div><div class="status-title">Error</div><div class="status-message">${msg}</div></div></div>`
      );
    }
  }, [onPresetsUpdated]);

  if (loading) {
    return (
      <div className="pyko-flex-center" style={{ padding: '2rem' }}>
        <div className="pyko-spinner" />
      </div>
    );
  }

  return (
    <div className="pyko-row">
      <div className="pyko-col">
        {/* Preset list */}
        <div className="pyko-glass-panel">
          <span className="caps-label">All Presets ({presets.length})</span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.75rem' }}>
            {presets.map((preset) => (
              <div
                key={preset.name}
                className="pyko-file-preview"
                style={{
                  cursor: 'pointer',
                  border: preset.name === currentPreset
                    ? '1px solid var(--pyko-moss)'
                    : '1px solid var(--pyko-glass-border)',
                }}
                onClick={() => handleSelect(preset)}
              >
                <span className="file-name" style={{ fontWeight: preset.name === currentPreset ? 600 : 400 }}>
                  {preset.name}
                </span>
                <span style={{ color: 'var(--pyko-text-muted)', fontSize: '0.75rem' }}>
                  {preset.lines} · {preset.max_chars}c/line · {preset.min_duration}s
                </span>
                <button
                  className="file-remove"
                  onClick={(e) => { e.stopPropagation(); handleDelete(preset.name); }}
                  title="Delete"
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="pyko-col">
        {/* Save new */}
        <div className="pyko-glass-panel">
          <span className="caps-label">Save Current as New Preset</span>
          <div className="pyko-flex-between" style={{ marginTop: '0.75rem' }}>
            <input
              className="pyko-input"
              type="text"
              placeholder="Preset name..."
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              style={{ flex: 1 }}
            />
            <button className="pyko-outline-button" onClick={handleSave} disabled={!newName.trim()}>
              Save
            </button>
          </div>
        </div>

        {/* Status */}
        <StatusCard html={statusHtml} />
      </div>
    </div>
  );
};

export default PresetManager;
