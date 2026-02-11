import { ref } from 'vue'
import { auth } from '../firebase'

export function useApiClient() {
    const loading = ref(false)
    const error = ref('')

    const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
        loading.value = true
        error.value = ''
        try {
            const user = auth.currentUser
            if (!user) {
                throw new Error('認証に失敗しました。再ログインしてください。')
            }
            const token = await user.getIdToken()

            const headers = {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }

            const res = await fetch(url, { ...options, headers })

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}))
                throw new Error(errData.detail || 'API request failed')
            }

            return await res.json()
        } catch (e: any) {
            error.value = e.message
            throw e
        } finally {
            loading.value = false
        }
    }

    return {
        loading,
        error,
        fetchWithAuth
    }
}
