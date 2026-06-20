import { apiClient } from './api';

export const securityService = {
  async getFindings(accountId: string, params?: Record<string, any>) {
    const response = await apiClient.get('/security/findings', {
      params: { account_id: accountId, ...params },
    });
    return response.data.data;
  },

  async getSecurityScore(accountId: string) {
    const response = await apiClient.get('/security/score', {
      params: { account_id: accountId },
    });
    return response.data.data;
  },

  async triggerScan(accountId: string) {
    const response = await apiClient.post('/security/scan', {
      account_id: accountId,
    });
    return response.data.data;
  },
};
