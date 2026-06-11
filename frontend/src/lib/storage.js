const KEY = "gatemind.session";

export function loadSession() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || { user: null, admin: null };
  } catch {
    return { user: null, admin: null };
  }
}

export function saveSession(session) {
  localStorage.setItem(KEY, JSON.stringify(session));
}
