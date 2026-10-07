import { api } from './api';

const API_BASE_URL = api.getBaseUrl();

export const documentApi = {
  /**
   * Uploads a document to the backend.
   * Calls POST /upload
   * 
   * @param {File} file - The file to upload.
   * @param {string} documentType - Supported types: 'company_policy', 'regulation', 'contract', 'sop'.
   * @param {string} documentVersion - Semantic version of the document (default '1.0.0').
   * @returns {Promise<object>} The upload summary response.
   */
  async uploadDocument(file, documentType, documentVersion = '1.0.0') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('document_version', documentVersion);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
      // Let the browser set Content-Type with correct multipart boundary automatically
    });

    if (!response.ok) {
      let errorMsg = 'Failed to upload document.';
      try {
        const data = await response.json();
        errorMsg = data.detail || data.message || errorMsg;
      } catch (e) {}
      throw new Error(errorMsg);
    }
    return response.json();
  },

  /**
   * Retrieves all indexed documents from PostgreSQL.
   * Calls GET /documents
   * 
   * @returns {Promise<Array>} The list of documents.
   */
  async getDocuments() {
    return api.get('/documents');
  },

  /**
   * Deletes a document by ID.
   * Calls DELETE /documents/{document_id}
   * 
   * @param {string} documentId - The UUID of the document to delete.
   * @returns {Promise<object>} The deletion confirmation message.
   */
  async deleteDocument(documentId) {
    return api.delete(`/documents/${documentId}`);
  }
};
