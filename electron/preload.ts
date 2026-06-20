/**
 * AWS Infra Vision - Preload Script
 * Exposes secure APIs to renderer process
 */

import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // System information
  getVersion: () => ipcRenderer.invoke('get-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // File operations
  selectFile: (options?: any) => ipcRenderer.invoke('select-file', options),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  exportData: (data: any, filename: string) => 
    ipcRenderer.invoke('export-data', data, filename),
  
  // External links
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  
  // Backend management
  restartBackend: () => ipcRenderer.invoke('restart-backend'),
  
  // Logging
  log: (level: string, message: string) => 
    ipcRenderer.invoke('log', level, message),
  
  // Platform detection
  isMac: process.platform === 'darwin',
  isWindows: process.platform === 'win32',
  isLinux: process.platform === 'linux',
});

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: {
      getVersion: () => Promise<string>;
      getPlatform: () => Promise<{ platform: string; arch: string; version: string }>;
      selectFile: (options?: any) => Promise<string[]>;
      selectDirectory: () => Promise<string[]>;
      exportData: (data: any, filename: string) => Promise<{ success: boolean; path?: string }>;
      openExternal: (url: string) => Promise<void>;
      restartBackend: () => Promise<{ success: boolean }>;
      log: (level: string, message: string) => Promise<void>;
      isMac: boolean;
      isWindows: boolean;
      isLinux: boolean;
    };
  }
}
