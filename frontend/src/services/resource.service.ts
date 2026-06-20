import { apiClient } from './api';

export const resourceService = {
  async getResources(accountId: string, params?: Record<string, any>) {
    const response = await apiClient.get('/resources/', {
      params: { account_id: accountId, ...params },
    });
    return response.data.data;
  },

  async getResourceStats(accountId: string) {
    const response = await apiClient.get('/resources/stats/summary', {
      params: { account_id: accountId },
    });
    return response.data.data;
  },

  async triggerScan(accountId: string, scanType = 'full') {
    const response = await apiClient.post('/resources/scan', {
      account_id: accountId,
      scan_type: scanType,
    });
    return response.data.data;
  },
};
