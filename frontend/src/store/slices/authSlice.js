import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { api } from "../../lib/api";
import { loadSession, saveSession } from "../../lib/storage";

const saved = loadSession();

export const loginUser = createAsyncThunk("auth/loginUser", async ({ email, password }) => {
  return api.loginUser(email, password);
});

export const loginAdmin = createAsyncThunk("auth/loginAdmin", async ({ email, password }) => {
  return api.loginAdmin(email, password);
});

const initialState = {
  user: saved.user || null,
  admin: saved.admin || null,
  status: "idle",
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    clearUserSession(state) {
      state.user = null;
      saveSession({ user: null, admin: state.admin });
    },
    clearAdminSession(state) {
      state.admin = null;
      saveSession({ user: state.user, admin: null });
    },
    clearAllSessions(state) {
      state.user = null;
      state.admin = null;
      saveSession({ user: null, admin: null });
    },
    setUserSession(state, action) {
      const payload = action.payload;
      state.user = payload
        ? {
            profile: payload.user,
            accessToken: payload.access_token,
            refreshToken: payload.refresh_token,
          }
        : null;
      saveSession({ user: state.user, admin: state.admin });
    },
    setAdminSession(state, action) {
      const payload = action.payload;
      state.admin = payload
        ? {
            profile: payload.admin,
            accessToken: payload.access_token,
            refreshToken: payload.refresh_token,
          }
        : null;
      saveSession({ user: state.user, admin: state.admin });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = "idle";
        state.user = {
          profile: action.payload.user,
          accessToken: action.payload.access_token,
          refreshToken: action.payload.refresh_token,
        };
        saveSession({ user: state.user, admin: state.admin });
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      })
      .addCase(loginAdmin.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(loginAdmin.fulfilled, (state, action) => {
        state.status = "idle";
        state.admin = {
          profile: action.payload.admin,
          accessToken: action.payload.access_token,
          refreshToken: action.payload.refresh_token,
        };
        saveSession({ user: state.user, admin: state.admin });
      })
      .addCase(loginAdmin.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      });
  },
});

export const { clearUserSession, clearAdminSession, clearAllSessions, setUserSession, setAdminSession } = authSlice.actions;
export default authSlice.reducer;
