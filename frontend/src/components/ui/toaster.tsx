import React from 'react';

export function Toaster() {
  return (
    <div id="toaster" className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {/* Toasts will be rendered here by the toast system */}
    </div>
  );
}

// Simple toast function for use throughout the app
export function toast({ title, description, variant = 'default' }: {
  title: string;
  description?: string;
  variant?: 'default' | 'destructive';
}) {
  const container = document.getElementById('toaster');
  if (!container) return;

  const el = document.createElement('div');
  el.className = `animate-in slide-in-from-right rounded-lg border px-4 py-3 shadow-lg ${
    variant === 'destructive' ? 'bg-red-900 border-red-700 text-red-100' : 'bg-slate-800 border-slate-700 text-white'
  }`;
  el.innerHTML = `<strong>${title}</strong>${description ? `<p class="text-sm mt-1 opacity-80">${description}</p>` : ''}`;
  container.appendChild(el);
  setTimeout(() => { el.remove(); }, 4000);
}
