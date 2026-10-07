import { api } from './api';

export const reviewApi = {
  /**
   * Retrieves details of a specific human-in-the-loop review request.
   * Calls GET /review/{review_id}
   * 
   * @param {string} reviewId - The ID of the review request.
   * @returns {Promise<object>} The review request details.
   */
  async getReview(reviewId) {
    return api.get(`/review/${reviewId}`);
  },

  /**
   * Submits a reviewer decision (approve, reject, request_more_evidence) and resumes graph.
   * Calls POST /review/{review_id}/decision
   * 
   * @param {string} reviewId - The ID of the review request.
   * @param {string} decision - Mapped values: 'approve', 'reject', 'request_more_evidence'.
   * @param {string} reviewerComment - Comments detailing why this action was selected.
   * @returns {Promise<object>} The decision application status outcome.
   */
  async submitReviewDecision(reviewId, decision, reviewerComment) {
    const actionMapping = {
      approve: 'continue',
      reject: 'terminate',
      request_more_evidence: 'retrieve_more_evidence'
    };
    
    const payload = {
      review_id: reviewId,
      decision: decision,
      reviewer_comment: reviewerComment,
      selected_action: actionMapping[decision] || 'continue'
    };
    return api.post(`/review/${reviewId}/decision`, payload);
  }
};
