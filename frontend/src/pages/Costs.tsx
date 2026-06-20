import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DollarSign } from 'lucide-react';

export default function Costs() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Costs</h1>
        <p className="text-slate-400 mt-1">AWS cost analytics and forecasting</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-green-500" />
            Cost Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Connect your AWS account with Cost Explorer access to see cost data.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
