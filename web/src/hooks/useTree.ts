import { useContext } from 'react'
import { TreeContext, type TreeContextValue } from '@/contexts/TreeContext'

export function useTree(): TreeContextValue {
  const ctx = useContext(TreeContext)
  if (!ctx) throw new Error('useTree must be used within <TreeProvider>')
  return ctx
}
