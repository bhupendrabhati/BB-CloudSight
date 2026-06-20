import { apiClient } from './api';

export const costService = {
  async getCostSummary(accountId: string, period = 'monthly') {
    const response = await apiClient.get('/costs/summary', {
      params: { account_id: accountId, period },
    });
    return response.data.data;
  },

  async getCostsByService(accountId: string) {
    const response = await apiClient.get('/costs/by-service', {
      params: { account_id: accountId },
    });
    return response.data.data;
  },

  async getCostForecast(accountId: string, months = 3) {
    const response = await apiClient.get('/costs/forecast', {
      params: { account_id: accountId, months },
    });
    return response.data.data;
  },
};
