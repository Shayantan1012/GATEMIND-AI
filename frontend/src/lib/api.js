const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const body = options.body;
  const isFormData = body instanceof FormData;

  if (!isFormData && body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: isFormData || body === undefined ? body : JSON.stringify(body),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.success === false) {
    throw new Error(payload.message || `Request failed with ${response.status}`);
  }
  return payload.data ?? payload;
}

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  health: () => request("/api/health"),

  registerUser: (data) => request("/api/auth/register", { method: "POST", body: data }),
  verifyOtp: (otp) => request("/api/auth/verify-otp", { method: "POST", body: { otp } }),
  loginUser: (email, password) => request("/api/auth/login", { method: "POST", body: { email, password } }),
  logoutUser: (refreshToken) => request("/api/auth/logout", { method: "POST", body: { refresh_token: refreshToken } }),
  forgotPassword: (email) => request("/api/auth/forgot-password", { method: "POST", body: { email } }),
  resetPassword: (otp, newPassword) => request("/api/auth/reset-password", { method: "POST", body: { otp, new_password: newPassword } }),

  getProfile: (token) => request("/api/users/profile", { headers: authHeaders(token) }),
  updateProfile: (token, data) => request("/api/users/profile", { method: "PUT", headers: authHeaders(token), body: data }),
  uploadProfileImage: (token, file) => {
    const formData = new FormData();
    formData.append("image", file);
    return request("/api/users/profile/image", { method: "POST", headers: authHeaders(token), body: formData });
  },
  changePassword: (token, data) => request("/api/users/change-password", { method: "POST", headers: authHeaders(token), body: data }),
  getProgress: (token) => request("/api/users/progress", { headers: authHeaders(token) }),

  registerAdmin: (data, bootstrapToken = "") =>
    request("/api/admin/auth/register", {
      method: "POST",
      headers: bootstrapToken ? { "X-Admin-Bootstrap-Token": bootstrapToken } : {},
      body: data,
    }),
  createAdminStaff: (token, data) =>
    request("/api/admin/staff", { method: "POST", headers: authHeaders(token), body: data }),
  listAdminStaff: (token) => request("/api/admin/staff", { headers: authHeaders(token) }),
  deleteAdminStaff: (token, id) =>
    request(`/api/admin/staff/${id}`, { method: "DELETE", headers: authHeaders(token) }),
  loginAdmin: (email, password) => request("/api/admin/auth/login", { method: "POST", body: { email, password } }),
  dashboard: (token) => request("/api/admin/dashboard", { headers: authHeaders(token) }),
  usersOverview: (token) => request("/api/admin/users", { headers: authHeaders(token) }),
  createQuestion: (token, data) => request("/api/admin/questions", { method: "POST", headers: authHeaders(token), body: data }),
  listQuestions: (token) => request("/api/admin/questions", { headers: authHeaders(token) }),
  createMockTest: (token, data) => request("/api/admin/mock-tests", { method: "POST", headers: authHeaders(token), body: data }),
  listAdminMockTests: (token) => request("/api/admin/mock-tests", { headers: authHeaders(token) }),
  updateMockTest: (token, id, data) => request(`/api/admin/mock-tests/${id}`, { method: "PUT", headers: authHeaders(token), body: data }),
  deleteMockTest: (token, id) => request(`/api/admin/mock-tests/${id}`, { method: "DELETE", headers: authHeaders(token) }),
  publishMockTest: (token, id) => request(`/api/admin/mock-tests/${id}/publish`, { method: "POST", headers: authHeaders(token) }),
  uploadDocument: (token, formData) => request("/api/admin/rag/documents", { method: "POST", headers: authHeaders(token), body: formData }),
  listDocuments: (token) => request("/api/admin/rag/documents", { headers: authHeaders(token) }),
  deleteDocument: (token, id) => request(`/api/admin/rag/documents/${id}`, { method: "DELETE", headers: authHeaders(token) }),
  clearAdminStorage: (token) => request("/api/admin/maintenance/storage", { method: "DELETE", headers: authHeaders(token) }),

  listMockTests: (token) => request("/api/mock-tests", { headers: authHeaders(token) }),
  getMockTest: (token, id) => request(`/api/mock-tests/${id}`, { headers: authHeaders(token) }),
  submitMockTest: (token, id, answers, timeTakenSeconds = 0) =>
    request(`/api/mock-tests/${id}/submit`, {
      method: "POST",
      headers: authHeaders(token),
      body: { answers, time_taken_seconds: timeTakenSeconds },
    }),
  mockHistory: (token) => request("/api/mock-tests/history", { headers: authHeaders(token) }),

  askRag: (token, query, filters, conversationId) =>
    request("/api/rag/chat", {
      method: "POST",
      headers: authHeaders(token),
      body: { query, filters, conversation_id: conversationId },
    }),
  ragHistory: (token) => request("/api/rag/history", { headers: authHeaders(token) }),
  createRagConversation: (token, title = "New chat") =>
    request("/api/rag/conversations", { method: "POST", headers: authHeaders(token), body: { title } }),
  listRagConversations: (token) => request("/api/rag/conversations", { headers: authHeaders(token) }),
  getRagConversationMessages: (token, id) => request(`/api/rag/conversations/${id}/messages`, { headers: authHeaders(token) }),
  deleteRagConversation: (token, id, documentIds = []) =>
    request(`/api/rag/conversations/${id}`, {
      method: "DELETE",
      headers: authHeaders(token),
      body: documentIds.length ? { document_ids: documentIds } : undefined,
    }),
  listRagDocuments: (token) => request("/api/rag/documents", { headers: authHeaders(token) }),
  uploadRagFiles: (token, files) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return request("/api/rag/documents", { method: "POST", headers: authHeaders(token), body: formData });
  },
};
