/**
 * AWS Infra Vision - Dashboard Page
 * Main overview of AWS infrastructure
 */
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  Server, DollarSign, Shield, AlertTriangle, 
  TrendingUp, Activity, Database, Cloud
} from 'lucide-react';

// Services
import { resourceService } from '../services/resource.service';
import { costService } from '../services/cost.service';
import { securityService } from '../services/security.service';

// Components
import ResourceGraph from '../components/visualization/ResourceGraph';
import AnomalyAlert from '../components/costs/AnomalyAlert';

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444'];

export default function Dashboard() {
  const [accountId, setAccountId] = useState<string>('');

  // Fetch resource stats
  const { data: resourceStats, isLoading: loadingResources } = useQuery({
    queryKey: ['resource-stats', accountId],
    queryFn: () => resourceService.getResourceStats(accountId),
    enabled: !!accountId,
  });

  // Fetch cost summary
  const { data: costSummary, isLoading: loadingCosts } = useQuery({
    queryKey: ['cost-summary', accountId],
    queryFn: () => costService.getCostSummary(accountId, 'monthly'),
    enabled: !!accountId,
  });

  // Fetch security findings
  const { data: securityFindings, isLoading: loadingSecurity } = useQuery({
    queryKey: ['security-findings', accountId],
    queryFn: () => securityService.getFindings(accountId, { status: 'open' }),
    enabled: !!accountId,
  });

  // Get account ID from localStorage or context
  useEffect(() => {
    const storedAccount = localStorage.getItem('active-account');
    if (storedAccount) {
      setAccountId(JSON.parse(storedAccount).account_id);
    }
  }, []);

  const statCards = [
    {
      title: 'Total Resources',
      value: resourceStats?.total_resources || 0,
      icon: Server,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Monthly Cost',
      value: `$${costSummary?.total_cost?.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      title: 'Security Issues',
      value: securityFindings?.findings?.length || 0,
      icon: Shield,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
    {
      title: 'FinOps Score',
      value: '78/100',
      icon: TrendingUp,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Overview of your AWS infrastructure
          </p>
        </div>
        <Button variant="outline" className="border-slate-700 text-slate-300">
          <Activity className="w-4 h-4 mr-2" />
          Refresh Data
        </Button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => (
          <Card key={index} className="bg-slate-900 border-slate-800">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">{stat.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">
                    {loadingResources || loadingCosts || loadingSecurity 
                      ? '...' 
                      : stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Alerts */}
      {securityFindings?.findings?.some((f: any) => f.severity === 'critical') && (
        <Card className="bg-red-500/10 border-red-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              <div>
                <p className="font-semibold text-red-400">Critical Security Issues Detected</p>
                <p className="text-sm text-red-300/70">
                  {securityFindings.findings.filter((f: any) => f.severity === 'critical').length} critical findings require immediate attention
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="bg-slate-900 border border-slate-800">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="costs">Cost Analysis</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="graph">Architecture Graph</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Resources by Service */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Database className="w-5 h-5 text-blue-500" />
                  Resources by Service
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={resourceStats?.by_service || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="service" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Cost by Region */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Cloud className="w-5 h-5 text-green-500" />
                  Cost by Region
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={costSummary?.by_region || []}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="cost"
                      nameKey="region"
                    >
                      {(costSummary?.by_region || []).map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Recent Security Findings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {securityFindings?.findings?.slice(0, 5).map((finding: any) => (
                  <div 
                    key={finding.id}
                    className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Badge 
                        variant={
                          finding.severity === 'critical' ? 'destructive' :
                          finding.severity === 'high' ? 'default' :
                          finding.severity === 'medium' ? 'secondary' : 'outline'
                        }
                      >
                        {finding.severity.toUpperCase()}
                      </Badge>
                      <span className="text-slate-300">{finding.title}</span>
                    </div>
                    <span className="text-sm text-slate-500">
                      {new Date(finding.detected_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
                {(!securityFindings?.findings || securityFindings.findings.length === 0) && (
                  <p className="text-slate-500 text-center py-8">No security findings</p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cost Analysis Tab */}
        <TabsContent value="costs">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Cost Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={costSummary?.daily_costs || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cost" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resources Tab */}
        <TabsContent value="resources">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="text-white">Resource Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {resourceStats?.by_type?.map((type: any) => (
                  <div key={type.type} className="p-4 bg-slate-800/50 rounded-lg">
                    <p className="text-sm text-slate-400">{type.type}</p>
                    <p className="text-2xl font-bold text-white">{type.count}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Graph Tab */}
        <TabsContent value="graph">
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-6">
              <ResourceGraph accountId={accountId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
