/**
 * SubLabel
 * 
 * Shared typography component for sandbox section sub-headings.
 */
export function SubLabel({ children }: { children: React.ReactNode }) {
    return (
      <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
        {children}
      </p>
    );
  }