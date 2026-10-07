import { api } from './api';

export const auditApi = {
  /**
   * Triggers a compliance audit query on the backend.
   * Calls POST /audit
   * 
   * @param {string} question - The user compliance audit query.
   * @returns {Promise<object>} The audit status and results.
   */
  async runAudit(question) {
    return api.post('/audit', { question });
  }
};
