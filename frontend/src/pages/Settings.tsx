import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Settings as SettingsIcon } from 'lucide-react';

export default function Settings() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">Application and account configuration</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <SettingsIcon className="w-5 h-5 text-slate-400" />
            AWS Account
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500">No AWS accounts configured yet.</p>
        </CardContent>
      </Card>
    </div>
  );
}
