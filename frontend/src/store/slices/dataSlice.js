import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { api } from "../../lib/api";

export const loadProfileBundle = createAsyncThunk("data/loadProfileBundle", async (token) => {
  const [profile, progress] = await Promise.all([api.getProfile(token), api.getProgress(token)]);
  return { profile, progress };
});

export const loadAdminBundle = createAsyncThunk("data/loadAdminBundle", async (token) => {
  const [dashboard, questions, documents] = await Promise.all([
    api.dashboard(token),
    api.listQuestions(token),
    api.listDocuments(token),
  ]);
  return { dashboard, questions, documents };
});

export const loadMockTestBundle = createAsyncThunk("data/loadMockTestBundle", async (token) => {
  const [mockTests, mockHistory] = await Promise.all([api.listMockTests(token), api.mockHistory(token)]);
  return { mockTests, mockHistory };
});

export const loadRagHistory = createAsyncThunk("data/loadRagHistory", async (token) => {
  return api.ragHistory(token);
});

export const loadUserRagDocuments = createAsyncThunk("data/loadUserRagDocuments", async (token) => {
  return api.listRagDocuments(token);
});

const dataSlice = createSlice({
  name: "data",
  initialState: {
    profile: null,
    progress: null,
    dashboard: null,
    questions: [],
    documents: [],
    mockTests: [],
    mockHistory: [],
    ragHistory: [],
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
        state.questions = action.payload.questions;
        state.documents = action.payload.documents;
        state.error = null;
      })
      .addCase(loadMockTestBundle.fulfilled, (state, action) => {
        state.mockTests = action.payload.mockTests;
        state.mockHistory = action.payload.mockHistory;
        state.error = null;
      })
      .addCase(loadRagHistory.fulfilled, (state, action) => {
        state.ragHistory = action.payload.reverse();
        state.error = null;
      })
      .addCase(loadUserRagDocuments.fulfilled, (state, action) => {
        state.userRagDocuments = action.payload;
        state.error = null;
      });
  },
});

export const { appendRagMessage, setActiveMockHistory, setProfile, setRagHistory } = dataSlice.actions;
export default dataSlice.reducer;
