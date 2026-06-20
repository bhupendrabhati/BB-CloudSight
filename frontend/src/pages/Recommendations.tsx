import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';

export default function Recommendations() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Recommendations</h1>
        <p className="text-slate-400 mt-1">Cost optimization and rightsizing recommendations</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            Optimization Opportunities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Recommendations will appear after running cost and resource analysis.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
