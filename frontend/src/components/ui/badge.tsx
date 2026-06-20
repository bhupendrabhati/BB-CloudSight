import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
}

const variants: Record<string, string> = {
  default: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  secondary: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
  destructive: 'bg-red-500/20 text-red-400 border-red-500/30',
  outline: 'bg-transparent text-slate-400 border-slate-600',
};

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}
