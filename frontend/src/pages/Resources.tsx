import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Server, RefreshCw } from 'lucide-react';

export default function Resources() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Resources</h1>
          <p className="text-slate-400 mt-1">Inventory of your AWS resources</p>
        </div>
        <Button variant="outline" className="border-slate-700 text-slate-300">
          <RefreshCw className="w-4 h-4 mr-2" />
          Start Scan
        </Button>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-blue-500" />
            Resource Inventory
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            Connect your AWS account and run a scan to see your resources here.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
