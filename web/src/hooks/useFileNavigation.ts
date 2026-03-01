import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * Returns a stable callback that normalises a vault path
 * and navigates to `/file/<relPath>`.
 */
export function useFileNavigation() {
  const navigate = useNavigate()

  const navigateToFile = useCallback(
    (rawPath: string) => {
      const vaultMarker = '/vault/'
      const idx = rawPath.indexOf(vaultMarker)
      const relPath = idx !== -1 ? rawPath.slice(idx + vaultMarker.length) : rawPath
      navigate('/file/' + relPath)
    },
    [navigate],
  )

  return navigateToFile
}
