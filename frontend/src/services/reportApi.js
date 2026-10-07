import { api } from './api';

const API_BASE_URL = api.getBaseUrl();

export const reportApi = {
  /**
   * Retrieves details of a persistent finalized or draft audit report.
   * Calls GET /reports/{report_id}
   * 
   * @param {string} reportId - The ID of the report.
   * @returns {Promise<object>} The audit report details.
   */
  async getReport(reportId) {
    return api.get(`/reports/${reportId}`);
  },

  /**
   * Retrieves the set of evidence sources referenced in the audit report.
   * Calls GET /reports/{report_id}/evidence
   * 
   * @param {string} reportId - The ID of the report.
   * @returns {Promise<Array>} The referenced evidence list.
   */
  async getReportEvidence(reportId) {
    return api.get(`/reports/${reportId}/evidence`);
  },

  /**
   * Returns the direct URL for downloading the report in Markdown.
   * Links to GET /reports/{report_id}/download
   * 
   * @param {string} reportId - The ID of the report.
   * @returns {string} The fully qualified download URL.
   */
  downloadReportUrl(reportId) {
    return `${API_BASE_URL}/reports/${reportId}/download`;
  },

  /**
   * Fetches the Markdown report binary stream and triggers native browser save action.
   * 
   * @param {string} reportId - The ID of the report to download.
   */
  async downloadReport(reportId) {
    const response = await fetch(this.downloadReportUrl(reportId));
    if (!response.ok) {
      throw new Error('Failed to compile or download report.');
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_report_${reportId}.md`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};
