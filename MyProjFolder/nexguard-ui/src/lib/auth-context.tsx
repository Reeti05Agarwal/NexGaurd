'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'

interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'admin' | 'analyst' | 'viewer'
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  signup: (name: string, email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  const login = useCallback(async (email: string, password: string) => {
    // Mock authentication
    await new Promise(resolve => setTimeout(resolve, 500))
    if (email && password) {
      setUser({
        id: '1',
        name: 'John Anderson',
        email,
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
        role: 'admin',
      })
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
  }, [])

  const signup = useCallback(async (name: string, email: string, password: string) => {
    // Mock signup
    await new Promise(resolve => setTimeout(resolve, 500))
    if (name && email && password) {
      setUser({
        id: '2',
        name,
        email,
        avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${name}`,
        role: 'analyst',
      })
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        signup,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}


export default useAuth;