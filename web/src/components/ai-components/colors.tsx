/**
 * ColorPalette — Sandbox Section
 *
 * Displays all CSS variable tokens from the design system.
 * Switch the theme in the navbar to verify light/dark responses.
 */
import { SectionHeader } from './section-header';

const COLOR_TOKENS = [
  { name: 'background', label: 'Background', var: '--background' },
  { name: 'foreground', label: 'Foreground', var: '--foreground' },
  { name: 'card', label: 'Card', var: '--card' },
  { name: 'card-foreground', label: 'Card Foreground', var: '--card-foreground' },
  { name: 'primary', label: 'Primary', var: '--primary' },
  { name: 'primary-foreground', label: 'Primary FG', var: '--primary-foreground' },
  { name: 'secondary', label: 'Secondary', var: '--secondary' },
  { name: 'secondary-foreground', label: 'Secondary FG', var: '--secondary-foreground' },
  { name: 'muted', label: 'Muted', var: '--muted' },
  { name: 'muted-foreground', label: 'Muted FG', var: '--muted-foreground' },
  { name: 'accent', label: 'Accent', var: '--accent' },
  { name: 'accent-foreground', label: 'Accent FG', var: '--accent-foreground' },
  { name: 'interactive', label: 'Interactive', var: '--interactive' },
  { name: 'interactive-foreground', label: 'Interactive FG', var: '--interactive-foreground' },
  { name: 'destructive', label: 'Destructive', var: '--destructive' },
  { name: 'destructive-foreground', label: 'Destructive FG', var: '--destructive-foreground' },
  { name: 'border', label: 'Border', var: '--border' },
  { name: 'input', label: 'Input', var: '--input' },
  { name: 'ring', label: 'Ring', var: '--ring' },
] as const;

export function ColorPalette() {
  return (
    <section className="space-y-6">
      <SectionHeader
        tag="01"
        title="Color Palette"
        description="All CSS variable tokens — switch the theme above to verify light/dark responses."
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {COLOR_TOKENS.map((token) => (
          <ColorSwatch key={token.name} token={token} />
        ))}
      </div>
    </section>
  );
}

function ColorSwatch({
  token,
}: {
  token: { name: string; label: string; var: string };
}) {
  return (
    <div className="flex flex-col gap-2">
      <div
        className="h-14 w-full rounded-md border border-border shadow-sm"
        style={{ backgroundColor: `hsl(var(${token.var}))` }}
      />
      <div>
        <p className="text-xs font-medium text-foreground leading-tight">
          {token.label}
        </p>
        <p className="text-[10px] text-muted-foreground font-mono leading-tight">
          {token.var}
        </p>
      </div>
    </div>
  );
}