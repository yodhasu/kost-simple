import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserStore, type UserProfile } from '../stores/userStore'

// Re-export types for backward compatibility
export type { UserProfile }

/**
 * Composable wrapper around the Pinia user store.
 * Provides backward compatibility with existing component usage.
 */
export function useAuth() {
  const store = useUserStore()
  const { user, userProfile, loading, error } = storeToRefs(store)

  return {
    // State (reactive refs)
    user,
    userProfile,
    loading,
    error,

    // Computed getters
    isAuthenticated: computed(() => store.isAuthenticated),
    userEmail: computed(() => store.userEmail),
    userDisplayName: computed(() => store.userDisplayName),
    userRole: computed(() => store.userRole),
    regionId: computed(() => store.regionId),

    // Actions
    signIn: store.signIn.bind(store),
    signOut: store.signOut.bind(store),
    getIdToken: store.getIdToken.bind(store),
    initAuth: store.initAuth.bind(store),
    fetchUserProfile: store.fetchUserProfile.bind(store),
  }
}

export default useAuth

