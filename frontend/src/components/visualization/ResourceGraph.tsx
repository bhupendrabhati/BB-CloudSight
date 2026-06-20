import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Server, Database, Globe, Cloud } from 'lucide-react';

interface ResourceGraphProps {
  accountId: string;
}

export default function ResourceGraph({ accountId }: ResourceGraphProps) {
  return (
    <div className="flex items-center justify-center h-64 text-slate-500">
      <div className="text-center">
        <Globe className="w-12 h-12 mx-auto mb-3 text-blue-500/50" />
        <p>Architecture visualization will appear here</p>
        <p className="text-sm mt-1">Run a resource scan to populate the graph</p>
      </div>
    </div>
  );
}
