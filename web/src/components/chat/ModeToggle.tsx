import { ChevronDown } from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import type { ChatMode } from '@/types'

interface ModeToggleProps {
  mode: ChatMode
  onChange: (mode: 'update' | 'search') => void
  disabled?: boolean
}

const LABELS: Record<'update' | 'search', string> = {
  update: 'Update',
  search: 'Search',
}

export function ModeToggle({ mode, onChange, disabled }: ModeToggleProps) {
  const currentLabel = mode === 'answering' ? 'Update' : LABELS[mode]

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        disabled={disabled}
        className={cn(
          'flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-lg border bg-background hover:bg-accent transition-colors',
          disabled && 'opacity-50 cursor-not-allowed',
        )}
      >
        {currentLabel}
        <ChevronDown className="h-3 w-3" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" side="top">
        <DropdownMenuItem onClick={() => onChange('update')}>Update</DropdownMenuItem>
        <DropdownMenuItem onClick={() => onChange('search')}>Search</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
