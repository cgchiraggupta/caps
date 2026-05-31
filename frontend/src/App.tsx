/* HinglishCaps — main App shell */

import React, { useState, useCallback } from 'react';
import './styles/pyko.css';
import { Preset } from './api';
import SingleVideoTab from './components/SingleVideoTab';
import BatchProcessingTab from './components/BatchProcessingTab';
import PresetManager from './components/PresetManager';

type Tab = 'single' | 'batch' | 'presets';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('single');
  const [currentPreset, setCurrentPreset] = useState<string>('Subtitle default');
  const [presets, setPresets] = useState<Preset[]>([]);
  const [presetSettings, setPresetSettings] = useState({
    word_level: false,
    transcription_engine: 'Whisper Large v3 (Recommended Quality)',
    enable_custom_replacements: false,
    custom_replacements_file: '',
    format_name: 'Subtitle',
    stream: 'None',
    style: 'None',
    max_chars: 42,
    min_duration: 3.0,
    gap_frames: 0,
    lines: 'Double',
    offset_seconds: -0.18,
  });

  const handlePresetChange = useCallback((presetName: string, settings: typeof presetSettings) => {
    setCurrentPreset(presetName);
    setPresetSettings(prev => ({ ...prev, ...settings }));
  }, []);

  return (
    <div className="app">
      {/* Nav */}
      <nav className="pyko-nav">
        <div className="pyko-nav-inner">
          <div className="pyko-brand">HinglishCaps</div>
          <div className="pyko-nav-links">
            <a
              href="#single"
              className={activeTab === 'single' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('single'); }}
            >
              Caption
            </a>
            <a
              href="#batch"
              className={activeTab === 'batch' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('batch'); }}
            >
              Batch
            </a>
            <a
              href="#presets"
              className={activeTab === 'presets' ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setActiveTab('presets'); }}
            >
              Presets
            </a>
          </div>
        </div>
      </nav>

      {/* Main */}
      <main className="pyko-main">
        <div className="pyko-container">
          <div className="pyko-hero pyko-fade-in">
            <p className="pyko-section-kicker">HinglishCaps</p>
            <h1>
              Captions,<br />
              <span className="italic">the right way</span>
            </h1>
            <p className="sub">
              Transcribe and caption your videos — in Hinglish and beyond.
            </p>
          </div>

          {/* Tabs */}
          <div className="pyko-tabs pyko-fade-in-delay">
            <div className="pyko-tab-nav">
              <button
                className={`pyko-tab ${activeTab === 'single' ? 'active' : ''}`}
                onClick={() => setActiveTab('single')}
              >
                Single Video
              </button>
              <button
                className={`pyko-tab ${activeTab === 'batch' ? 'active' : ''}`}
                onClick={() => setActiveTab('batch')}
              >
                Batch Processing
              </button>
              <button
                className={`pyko-tab ${activeTab === 'presets' ? 'active' : ''}`}
                onClick={() => setActiveTab('presets')}
              >
                Presets
              </button>
            </div>

            <div className={`pyko-tab-content ${activeTab === 'single' ? 'active' : ''}`}>
              <SingleVideoTab
                currentPreset={currentPreset}
                presetSettings={presetSettings}
                onPresetChange={handlePresetChange}
              />
            </div>

            <div className={`pyko-tab-content ${activeTab === 'batch' ? 'active' : ''}`}>
              <BatchProcessingTab
                currentPreset={currentPreset}
                presetSettings={presetSettings}
                onPresetChange={handlePresetChange}
              />
            </div>

            <div className={`pyko-tab-content ${activeTab === 'presets' ? 'active' : ''}`}>
              <PresetManager
                presets={presets}
                currentPreset={currentPreset}
                onPresetChange={handlePresetChange}
                onPresetsUpdated={setPresets}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="pyko-footer">
        <div className="pyko-container pyko-footer-grid">
          <div>
            <h4>HinglishCaps</h4>
            <p style={{ color: 'var(--pyko-text-muted)', fontSize: '0.875rem' }}>
              Video caption generation, made simple.
            </p>
          </div>
          <div>
            <h4>Tech</h4>
            <ul>
              <li><a href="https://fastapi.tiangolo.com/" target="_blank" rel="noopener noreferrer">FastAPI</a></li>
              <li><a href="https://react.dev/" target="_blank" rel="noopener noreferrer">React</a></li>
              <li><a href="https://openai.com/index/whisper/" target="_blank" rel="noopener noreferrer">Whisper</a></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
