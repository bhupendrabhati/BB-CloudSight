/**
 * AWS Infra Vision - Main Application Component
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';

// Layout
import MainLayout from './components/layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Costs from './pages/Costs';
import Security from './pages/Security';
import Terraform from './pages/Terraform';
import CloudFormation from './pages/CloudFormation';
import Recommendations from './pages/Recommendations';
import Timeline from './pages/Timeline';
import Settings from './pages/Settings';
import SetupWizard from './pages/SetupWizard';

// Store
import { useAuthStore } from './store/authSlice';

// API Client
import { apiClient } from './services/api';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading AWS Infra Vision...</p>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Setup Wizard - shown when no accounts configured */}
          <Route path="/setup" element={<SetupWizard />} />
          
          {/* Main Application Routes */}
          <Route path="/" element={isAuthenticated ? <MainLayout /> : <Navigate to="/setup" />}>
            <Route index element={<Dashboard />} />
            <Route path="resources" element={<Resources />} />
            <Route path="costs" element={<Costs />} />
            <Route path="security" element={<Security />} />
            <Route path="terraform" element={<Terraform />} />
            <Route path="cloudformation" element={<CloudFormation />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="timeline" element={<Timeline />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Toaster />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
