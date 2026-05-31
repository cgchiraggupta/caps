/* API client for HinglishCaps backend */

import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  timeout: 120_000,
});

/* --- Types --- */

export interface Preset {
  name: string;
  format_name: string;
  stream: string;
  style: string;
  max_chars: number;
  min_duration: number;
  gap_frames: number;
  lines: string;
}

export interface PresetSavePayload {
  name: string;
  format_name: string;
  stream: string;
  style: string;
  max_chars: number;
  min_duration: number;
  gap_frames: number;
  lines: string;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'running' | 'done' | 'error';
  progress: number;
  total: number;
  result_zip: string | null;
  result_file: string | null;
  result_filename: string | null;
  status_html: string | null;
  error: string | null;
}

export interface JobStarted {
  job_id: string;
  status: string;
}

/* --- Presets --- */

export async function getPresets(): Promise<Preset[]> {
  const { data } = await client.get<Preset[]>('/presets');
  return data;
}

export async function getPresetChoices(): Promise<string[]> {
  const { data } = await client.get<string[]>('/presets/choices');
  return data;
}

export async function getPreset(name: string): Promise<Preset> {
  const { data } = await client.get<Preset>(`/presets/${encodeURIComponent(name)}`);
  return data;
}

export async function savePreset(payload: PresetSavePayload): Promise<void> {
  await client.post('/presets', payload);
}

export async function deletePreset(name: string): Promise<void> {
  await client.delete(`/presets/${encodeURIComponent(name)}`);
}

/* --- Single Caption --- */

export async function startSingleJob(
  video: File,
  params: Record<string, string | boolean | number>
): Promise<JobStarted> {
  const form = new FormData();
  form.append('video', video);
  for (const [key, value] of Object.entries(params)) {
    form.append(key, String(value));
  }

  const { data } = await client.post<JobStarted>('/captions', form);
  return data;
}

/* --- Batch Caption --- */

export async function startBatchJob(
  videos: File[],
  params: Record<string, string | boolean | number>
): Promise<JobStarted> {
  const form = new FormData();
  for (const video of videos) {
    form.append('videos', video);
  }
  for (const [key, value] of Object.entries(params)) {
    form.append(key, String(value));
  }

  const { data } = await client.post<JobStarted>('/captions/batch', form);
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const { data } = await client.get<JobStatus>(`/jobs/${jobId}`);
  return data;
}

export async function deleteJob(jobId: string): Promise<void> {
  await client.delete(`/jobs/${jobId}`);
}

export function getDownloadUrl(jobId: string, filename: string): string {
  return `/api/download/${encodeURIComponent(jobId)}/${encodeURIComponent(filename)}`;
}
