import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen } from 'lucide-react';

export default function Terraform() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Terraform</h1>
        <p className="text-slate-400 mt-1">Terraform state integration and drift detection</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-500" />
            Terraform Managed Resources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Terraform integration will be available soon.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
