import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Cloud, Key, User, Shield } from 'lucide-react';

export default function SetupWizard() {
  const [step, setStep] = useState(0);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <Card className="bg-slate-900 border-slate-800 max-w-lg w-full">
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <Cloud className="w-8 h-8 text-blue-500" />
            <CardTitle className="text-2xl font-bold text-white">AWS Infra Vision</CardTitle>
          </div>
          <p className="text-slate-400 text-sm">
            Connect your AWS account to get started with infrastructure intelligence.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-3">
            <Button variant="outline" className="h-16 justify-start gap-3 border-slate-700 text-slate-300">
              <Key className="w-5 h-5 text-blue-500" />
              <div className="text-left">
                <p className="font-medium text-white">Access Keys</p>
                <p className="text-xs text-slate-500">Use AWS Access Key ID and Secret</p>
              </div>
            </Button>
            <Button variant="outline" className="h-16 justify-start gap-3 border-slate-700 text-slate-300">
              <User className="w-5 h-5 text-green-500" />
              <div className="text-left">
                <p className="font-medium text-white">AWS Profile</p>
                <p className="text-xs text-slate-500">Use named profile from ~/.aws/config</p>
              </div>
            </Button>
            <Button variant="outline" className="h-16 justify-start gap-3 border-slate-700 text-slate-300">
              <Shield className="w-5 h-5 text-purple-500" />
              <div className="text-left">
                <p className="font-medium text-white">IAM Role</p>
                <p className="text-xs text-slate-500">Use cross-account IAM role</p>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
