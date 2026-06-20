import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Cloud } from 'lucide-react';

export default function CloudFormation() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">CloudFormation</h1>
        <p className="text-slate-400 mt-1">CloudFormation stack management</p>
      </div>
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Cloud className="w-5 h-5 text-orange-500" />
            CloudFormation Stacks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-500 text-center py-12">
            CloudFormation integration will be available soon.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
