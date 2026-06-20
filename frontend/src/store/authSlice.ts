import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  accountId: string | null;
  setAuthenticated: (accountId: string) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  isLoading: false,
  accountId: null,
  setAuthenticated: (accountId: string) => {
    localStorage.setItem('active-account', JSON.stringify({ account_id: accountId }));
    set({ isAuthenticated: true, isLoading: false, accountId });
  },
  setLoading: (isLoading: boolean) => set({ isLoading }),
  logout: () => {
    localStorage.removeItem('active-account');
    set({ isAuthenticated: false, accountId: null });
  },
}));
