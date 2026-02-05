import { ref, computed } from 'vue'
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

// State
const user = ref<User | null>(null)
const userProfile = ref<UserProfile | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Computed
const isAuthenticated = computed(() => !!user.value)
const userEmail = computed(() => user.value?.email || '')
const userDisplayName = computed(() => userProfile.value?.name || user.value?.displayName || 'User')
const userRole = computed(() => userProfile.value?.role || '')

// Initialize auth state listener
export function initAuth() {
  return new Promise<User | null>((resolve) => {
    onAuthStateChanged(auth, async (firebaseUser) => {
      user.value = firebaseUser
      
      if (firebaseUser) {
        try {
          await fetchUserProfile()
        } catch (e) {
          console.error('Failed to fetch user profile:', e)
        }
      } else {
        userProfile.value = null
      }
      
      loading.value = false
      resolve(firebaseUser)
    })
  })
}

// Fetch user profile from backend
async function fetchUserProfile() {
  try {
    const response = await httpClient.get<UserProfile>('/users/me')
    userProfile.value = response.data
    return response.data
  } catch (err) {
    console.error('Error fetching user profile:', err)
    throw err
  }
}

// Sign in with email and password
export async function signIn(email: string, password: string): Promise<User> {
  error.value = null
  loading.value = true
  
  try {
    const credential = await signInWithEmailAndPassword(auth, email, password)
    user.value = credential.user
    await fetchUserProfile()
    return credential.user
  } catch (err: any) {
    error.value = getErrorMessage(err.code)
    throw err
  } finally {
    loading.value = false
  }
}

// Sign out
export async function signOut(): Promise<void> {
  try {
    await firebaseSignOut(auth)
    user.value = null
    userProfile.value = null
  } catch (err: any) {
    console.error('Sign out error:', err)
    throw err
  }
}

// Get current user's ID token
export async function getIdToken(): Promise<string | null> {
  if (!user.value) return null
  return user.value.getIdToken()
}

// Get error message from Firebase error code
function getErrorMessage(code: string): string {
  const messages: Record<string, string> = {
    'auth/invalid-email': 'Email tidak valid',
    'auth/user-disabled': 'Akun telah dinonaktifkan',
    'auth/user-not-found': 'Email tidak terdaftar',
    'auth/wrong-password': 'Password salah',
    'auth/invalid-credential': 'Email atau password salah',
    'auth/too-many-requests': 'Terlalu banyak percobaan, coba lagi nanti',
  }
  return messages[code] || 'Terjadi kesalahan, silakan coba lagi'
}

// Export reactive state
export function useAuth() {
  return {
    user,
    userProfile,
    loading,
    error,
    isAuthenticated,
    userEmail,
    userDisplayName,
    userRole,
    signIn,
    signOut,
    getIdToken,
    initAuth,
    fetchUserProfile,
  }
}

export default useAuth
