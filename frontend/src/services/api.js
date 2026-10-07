const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = 'An error occurred while processing your request.';
    try {
      const data = await response.json();
      errorMsg = data.detail || data.message || errorMsg;
    } catch (e) {
      // Response is not JSON
    }
    throw new Error(errorMsg);
  }
  return response.json();
}

export const api = {
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      return await handleResponse(response);
    } catch (error) {
      console.error(`API GET error on ${endpoint}:`, error);
      throw error;
    }
  },

  async post(endpoint, body) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      return await handleResponse(response);
    } catch (error) {
      console.error(`API POST error on ${endpoint}:`, error);
      throw error;
    }
  },

  async put(endpoint, body) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      return await handleResponse(response);
    } catch (error) {
      console.error(`API PUT error on ${endpoint}:`, error);
      throw error;
    }
  },

  async delete(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
      });
      return await handleResponse(response);
    } catch (error) {
      console.error(`API DELETE error on ${endpoint}:`, error);
      throw error;
    }
  },

  getBaseUrl() {
    return API_BASE_URL;
  }
};
