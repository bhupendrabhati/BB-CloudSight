import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Clock } from 'lucide-react';

export default function Timeline() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Timeline</h1>
        <p className="text-slate-400 mt-1">Infrastructure change history</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-cyan-500" />
            Event Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Timeline events will appear after enabling CloudTrail integration.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
