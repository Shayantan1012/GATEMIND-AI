import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { api } from "../../lib/api";

export const loadProfileBundle = createAsyncThunk("data/loadProfileBundle", async (token) => {
  const [profile, progress] = await Promise.all([api.getProfile(token), api.getProgress(token)]);
  return { profile, progress };
});

export const loadAdminBundle = createAsyncThunk("data/loadAdminBundle", async ({ token, role }) => {
  const can = (...roles) => role === "SUPER_ADMIN" || roles.includes(role);
  const [dashboard, usersOverview, documents, mockTests] = await Promise.all([
    can("ANALYTICS_ADMIN") ? api.dashboard(token) : Promise.resolve(null),
    can("ANALYTICS_ADMIN", "SUPPORT_ADMIN") ? api.usersOverview(token) : Promise.resolve([]),
    can("CONTENT_ADMIN", "ANALYTICS_ADMIN") ? api.listDocuments(token) : Promise.resolve([]),
    can("MOCKTEST_ADMIN", "ANALYTICS_ADMIN") ? api.listAdminMockTests(token) : Promise.resolve([]),
  ]);
  return { dashboard, usersOverview, documents, mockTests };
});

export const loadMockTestBundle = createAsyncThunk("data/loadMockTestBundle", async (token) => {
  const [mockTests, mockHistory] = await Promise.all([api.listMockTests(token), api.mockHistory(token)]);
  return { mockTests, mockHistory };
});

export const loadRagHistory = createAsyncThunk("data/loadRagHistory", async (token) => {
  return api.ragHistory(token);
});

export const loadRagConversations = createAsyncThunk("data/loadRagConversations", async (token) => {
  return api.listRagConversations(token);
});

export const loadRagConversationMessages = createAsyncThunk(
  "data/loadRagConversationMessages",
  async ({ token, conversationId }) => {
    const messages = await api.getRagConversationMessages(token, conversationId);
    return { conversationId, messages };
  },
);

export const loadUserRagDocuments = createAsyncThunk("data/loadUserRagDocuments", async (token) => {
  return api.listRagDocuments(token);
});

const dataSlice = createSlice({
  name: "data",
  initialState: {
    profile: null,
    progress: null,
    dashboard: null,
    usersOverview: [],
    questions: [],
    documents: [],
    mockTests: [],
    mockHistory: [],
    ragHistory: [],
    ragConversations: [],
    activeRagConversationId: null,
    userRagDocuments: [],
    status: "idle",
    error: null,
  },
  reducers: {
    setProfile(state, action) {
      state.profile = action.payload;
    },
    setRagHistory(state, action) {
      state.ragHistory = action.payload;
    },
    appendRagMessage(state, action) {
      state.ragHistory.push(action.payload);
    },
    setActiveRagConversation(state, action) {
      state.activeRagConversationId = action.payload;
      state.ragHistory = [];
    },
    upsertRagConversation(state, action) {
      const conversation = action.payload;
      const index = state.ragConversations.findIndex((item) => item.conversation_id === conversation.conversation_id);
      if (index >= 0) state.ragConversations[index] = conversation;
      else state.ragConversations.unshift(conversation);
      state.ragConversations.sort((a, b) => String(b.updated_at).localeCompare(String(a.updated_at)));
    },
    removeRagConversation(state, action) {
      state.ragConversations = state.ragConversations.filter((item) => item.conversation_id !== action.payload);
      if (state.activeRagConversationId === action.payload) {
        state.activeRagConversationId = null;
        state.ragHistory = [];
      }
    },
    setActiveMockHistory(state, action) {
      state.mockHistory = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loadProfileBundle.fulfilled, (state, action) => {
        state.profile = action.payload.profile;
        state.progress = action.payload.progress;
        state.error = null;
      })
      .addCase(loadAdminBundle.fulfilled, (state, action) => {
        state.dashboard = action.payload.dashboard;
        state.usersOverview = action.payload.usersOverview;
        state.documents = action.payload.documents;
        state.mockTests = action.payload.mockTests;
        state.error = null;
      })
      .addCase(loadMockTestBundle.fulfilled, (state, action) => {
        state.mockTests = action.payload.mockTests;
        state.mockHistory = action.payload.mockHistory;
        state.error = null;
      })
      .addCase(loadRagHistory.fulfilled, (state, action) => {
        state.ragHistory = action.payload;
        state.error = null;
      })
      .addCase(loadRagConversations.fulfilled, (state, action) => {
        state.ragConversations = action.payload;
        state.error = null;
      })
      .addCase(loadRagConversationMessages.fulfilled, (state, action) => {
        if (state.activeRagConversationId === action.payload.conversationId) {
          state.ragHistory = action.payload.messages;
        }
        state.error = null;
      })
      .addCase(loadUserRagDocuments.fulfilled, (state, action) => {
        state.userRagDocuments = action.payload;
        state.error = null;
      });
  },
});

export const {
  appendRagMessage,
  removeRagConversation,
  setActiveMockHistory,
  setActiveRagConversation,
  setProfile,
  setRagHistory,
  upsertRagConversation,
} = dataSlice.actions;
export default dataSlice.reducer;
