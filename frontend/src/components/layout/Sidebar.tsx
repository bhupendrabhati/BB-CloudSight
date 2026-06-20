import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Server, DollarSign, Shield, BookOpen,
  Cloud, Lightbulb, Clock, Settings, Activity
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/resources', label: 'Resources', icon: Server },
  { path: '/costs', label: 'Costs', icon: DollarSign },
  { path: '/security', label: 'Security', icon: Shield },
  { path: '/terraform', label: 'Terraform', icon: BookOpen },
  { path: '/cloudformation', label: 'CloudFormation', icon: Cloud },
  { path: '/recommendations', label: 'Recommendations', icon: Lightbulb },
  { path: '/timeline', label: 'Timeline', icon: Clock },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <aside className="w-56 border-r border-slate-800 bg-slate-900/50 flex flex-col">
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </button>
          );
        })}
      </nav>
      <div className="border-t border-slate-800 p-3">
        <div className="flex items-center gap-2 px-3 py-2 text-xs text-slate-500">
          <Activity className="h-3 w-3" />
          AWS Infra Vision v1.0.0
        </div>
      </div>
    </aside>
  );
}
