/**
 * hooks/useAuth.ts
 * Authentication state, login, register, logout.
 */

import { useState, useCallback } from "react";
import { useRouter } from "next/router";
import { authAPI } from "@/services/api";

export function useAuth() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      await authAPI.login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  const register = useCallback(
    async (email: string, password: string, name: string) => {
      setLoading(true);
      setError(null);
      try {
        await authAPI.register(email, password, name);
        router.push("/");
      } catch (err: any) {
        setError(err?.response?.data?.detail ?? "Registration failed. Try a different email.");
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(() => {
    authAPI.logout();
  }, []);

  return {
    isAuthenticated: authAPI.isAuthenticated(),
    login,
    register,
    logout,
    loading,
    error,
    clearError: () => setError(null),
  };
}
