/**
 * SectionHeader
 *
 * Reusable header for sandbox sections.
 * Used by all UI sections (color palette, typography, components, etc.)
 */
export function SectionHeader({
    tag,
    title,
    description,
  }: {
    tag: string;
    title: string;
    description: string;
  }) {
    return (
      <div className="flex items-start gap-4 pb-4 border-b border-border">
        <span className="text-xs font-mono text-muted-foreground mt-1 tabular-nums">
          {tag}
        </span>
        <div>
          <h2 className="font-serif text-2xl font-bold text-foreground">
            {title}
          </h2>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
      </div>
    );
  }