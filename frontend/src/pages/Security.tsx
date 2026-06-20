import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield } from 'lucide-react';

export default function Security() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Security</h1>
        <p className="text-slate-400 mt-1">Security findings and compliance</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-red-500" />
            Security Findings
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Run a security scan to identify misconfigurations and risks.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
