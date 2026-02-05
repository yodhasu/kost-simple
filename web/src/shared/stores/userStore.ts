import { defineStore } from 'pinia'
import { 
  signInWithEmailAndPassword, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User
} from 'firebase/auth'
import { auth } from '../../lib/firebase'
import httpClient from '../utils/api/httpClient'

export interface UserProfile {
  id: string
  firebase_uid: string
  name: string
  role: string
  region_id: string | null
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    userProfile: null as UserProfile | null,
    selectedRegionId: localStorage.getItem('selected_region_id') as string | null,
    loading: true,
    error: null as string | null,
    _authInitialized: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    // Use selected region (owner override) OR assigned region
    regionId: (state) => state.selectedRegionId || state.userProfile?.region_id || null,
    userEmail: (state) => state.user?.email ?? '',
    userDisplayName: (state) => state.userProfile?.name ?? state.user?.displayName ?? 'User',
    userRole: (state) => state.userProfile?.role ?? '',
  },

  actions: {
    /**
     * Initialize auth state listener.
     * Call this once on app startup.
     */
    initAuth(): Promise<User | null> {
      return new Promise((resolve) => {
        if (this._authInitialized) {
          resolve(this.user)
          return
        }

        onAuthStateChanged(auth, async (firebaseUser) => {
          this.user = firebaseUser
          
          if (firebaseUser) {
            try {
              await this.fetchUserProfile()
            } catch (e) {
              console.error('Failed to fetch user profile:', e)
            }
          } else {
            this.userProfile = null
          }
          
          this.loading = false
          this._authInitialized = true
          resolve(firebaseUser)
        })
      })
    },

    /**
     * Fetch user profile from backend /users/me endpoint.
     */
    async fetchUserProfile(): Promise<UserProfile> {
      try {
        const response = await httpClient.get<UserProfile>('/users/me')
        this.userProfile = response.data
        return response.data
      } catch (err) {
        console.error('Error fetching user profile:', err)
        throw err
      }
    },

    /**
     * Sign in with email and password.
     */
    async signIn(email: string, password: string): Promise<User> {
      this.error = null
      this.loading = true
      
      try {
        const credential = await signInWithEmailAndPassword(auth, email, password)
        this.user = credential.user
        await this.fetchUserProfile()
        return credential.user
      } catch (err: any) {
        this.error = this._getErrorMessage(err.code)
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * Sign out the current user.
     */
    async signOut(): Promise<void> {
      try {
        await firebaseSignOut(auth)
        this.user = null
        this.userProfile = null
      } catch (err) {
        console.error('Sign out error:', err)
        throw err
      }
    },

    /**
     * Get current user's ID token for API calls.
     */
    async getIdToken(): Promise<string | null> {
      if (!this.user) return null
      return this.user.getIdToken()
    },

    /**
     * Get error message from Firebase error code.
     */
    _getErrorMessage(code: string): string {
      const messages: Record<string, string> = {
        'auth/invalid-email': 'Email tidak valid',
        'auth/user-disabled': 'Akun telah dinonaktifkan',
        'auth/user-not-found': 'Email tidak terdaftar',
        'auth/wrong-password': 'Password salah',
        'auth/invalid-credential': 'Email atau password salah',
        'auth/too-many-requests': 'Terlalu banyak percobaan, coba lagi nanti',
      }
      return messages[code] || 'Terjadi kesalahan, silakan coba lagi'
    },
  },
})
