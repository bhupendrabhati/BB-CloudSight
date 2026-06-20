/**
 * AWS Infra Vision - Electron Main Process
 * Manages application lifecycle and IPC communication
 */

import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';

let mainWindow: BrowserWindow | null = null;
let backendProcess: ChildProcess | null = null;

const isDev = !app.isPackaged;
const BACKEND_PORT = 8000;

/**
 * Create the main application window
 */
function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    show: false,
    backgroundColor: '#0f172a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    titleBarStyle: 'hiddenInset',
    frame: true,
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'));
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Start the FastAPI backend server
 */
async function startBackend(): Promise<void> {
  return new Promise((resolve, reject) => {
    const pythonPath = isDev 
      ? path.join(process.cwd(), '.venv', 'bin', 'python') 
      : path.join(process.resourcesPath, 'python', 'python');
    
    const backendScript = isDev
      ? path.join(__dirname, '../../backend/app/main.py')
      : path.join(process.resourcesPath, 'backend', 'app', 'main.py');

    backendProcess = spawn(pythonPath, [backendScript], {
      cwd: path.dirname(backendScript),
      env: {
        ...process.env,
        PYTHONPATH: path.dirname(backendScript),
      },
    });

    backendProcess.stdout?.on('data', (data) => {
      console.log(`Backend: ${data}`);
      
      // Check if backend is ready
      if (data.toString().includes('Uvicorn running')) {
        resolve();
      }
    });

    backendProcess.stderr?.on('data', (data) => {
      console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      reject(error);
    });

    backendProcess.on('exit', (code) => {
      console.log(`Backend exited with code ${code}`);
    });

    // Timeout after 10 seconds
    setTimeout(() => {
      reject(new Error('Backend startup timeout'));
    }, 10000);
  });
}

/**
 * Stop the backend server
 */
function stopBackend(): void {
  if (backendProcess) {
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
}

/**
 * IPC Handlers
 */
function setupIpcHandlers(): void {
  // Open external URLs
  ipcMain.handle('open-external', async (_, url: string) => {
    await shell.openExternal(url);
  });

  // File dialog for Terraform state files
  ipcMain.handle('select-file', async (_, options) => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openFile'],
      filters: [
        { name: 'Terraform State', extensions: ['tfstate', 'json'] },
        { name: 'All Files', extensions: ['*'] },
      ],
      ...options,
    });
    return result.filePaths;
  });

  // Select directory
  ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog(mainWindow!, {
      properties: ['openDirectory'],
    });
    return result.filePaths;
  });

  // Get app version
  ipcMain.handle('get-version', () => {
    return app.getVersion();
  });

  // Get platform info
  ipcMain.handle('get-platform', () => {
    return {
      platform: process.platform,
      arch: process.arch,
      version: process.version,
    };
  });

  // Restart backend
  ipcMain.handle('restart-backend', async () => {
    stopBackend();
    await new Promise(resolve => setTimeout(resolve, 1000));
    await startBackend();
    return { success: true };
  });

  // Export data
  ipcMain.handle('export-data', async (_, data: any, filename: string) => {
    const result = await dialog.showSaveDialog(mainWindow!, {
      defaultPath: filename,
      filters: [
        { name: 'JSON', extensions: ['json'] },
        { name: 'CSV', extensions: ['csv'] },
      ],
    });

    if (result.filePath) {
      fs.writeFileSync(result.filePath, JSON.stringify(data, null, 2));
      return { success: true, path: result.filePath };
    }
    return { success: false };
  });

  // Log message
  ipcMain.handle('log', (_, level: string, message: string) => {
    console.log(`[${level}] ${message}`);
  });
}

/**
 * Application lifecycle
 */
app.whenReady().then(async () => {
  try {
    // Start backend first
    console.log('Starting backend server...');
    await startBackend();
    console.log('Backend server started');

    // Setup IPC handlers
    setupIpcHandlers();

    // Create window
    createWindow();

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
      }
    });
  } catch (error) {
    console.error('Failed to start application:', error);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopBackend();
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Rejection:', reason);
});
