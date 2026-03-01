'use client';

import { useState } from 'react';
import { SectionHeader } from './section-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  ArrowUp,
  Upload,
  FileText,
  ArrowRight,
  ExternalLink,
  Plus,
  Settings,
  Search,
  Loader2,
  Check,
  Scale,
  Globe,
  Copy,
  Trash2,
  Download,
} from 'lucide-react';

export function ComponentsShowcase() {
  return (
    <TooltipProvider delayDuration={200}>
      <section className="space-y-12">
        <SectionHeader
          tag="03"
          title="Components"
          description="shadcn/ui primitives rendered against the live design system."
        />

        <ButtonShowcase />
        <ButtonWithIconsShowcase />
        <ButtonLoadingShowcase />
        <TooltipShowcase />
        <BadgeShowcase />
        <InputShowcase />
        <CardShowcase />
      </section>
    </TooltipProvider>
  );
}

// ─── Buttons — variants ──────────────────────────────────────────────────────

function ButtonShowcase() {
  return (
    <div className="space-y-4">
      <SubLabel>Button — variants</SubLabel>
      <div className="flex flex-wrap gap-3">
        <Button variant="default">Default</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="interactive">Interactive</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="link">Link</Button>
        <Button disabled>Disabled</Button>
      </div>

      <SubLabel>Button — sizes</SubLabel>
      <div className="flex flex-wrap items-center gap-3">
        <Button size="lg">Large</Button>
        <Button size="default">Default</Button>
        <Button size="sm">Small</Button>
      </div>
    </div>
  );
}

// ─── Buttons — with icons ────────────────────────────────────────────────────

function ButtonWithIconsShowcase() {
  return (
    <div className="space-y-4">
      <SubLabel>Button — icon left</SubLabel>
      <div className="flex flex-wrap gap-3">
        <Button>
          <ArrowUp /> Send Message
        </Button>
        <Button variant="interactive">
          <Upload /> Upload Document
        </Button>
        <Button variant="outline">
          <FileText /> New Contract
        </Button>
        <Button variant="secondary">
          <Globe /> Australia
        </Button>
        <Button variant="destructive">
          <Trash2 /> Delete
        </Button>
      </div>

      <SubLabel>Button — icon right</SubLabel>
      <div className="flex flex-wrap gap-3">
        <Button>
          Continue <ArrowRight />
        </Button>
        <Button variant="interactive">
          Explore <ExternalLink />
        </Button>
        <Button variant="outline">
          Download <Download />
        </Button>
        <Button variant="ghost">
          View all <ArrowRight />
        </Button>
      </div>

      <SubLabel>Button — icon only</SubLabel>
      <div className="flex flex-wrap items-center gap-3">
        <Button size="icon">
          <Plus />
        </Button>
        <Button size="icon" variant="secondary">
          <Settings />
        </Button>
        <Button size="icon" variant="outline">
          <Search />
        </Button>
        <Button size="icon" variant="interactive">
          <ArrowUp />
        </Button>
        <Button size="icon" variant="ghost">
          <Copy />
        </Button>
        <Button size="icon" variant="destructive">
          <Trash2 />
        </Button>
      </div>
    </div>
  );
}

// ─── Buttons — loading states ────────────────────────────────────────────────

function ButtonLoadingShowcase() {
  const [loading1, setLoading1] = useState(false);
  const [loading2, setLoading2] = useState(false);
  const [success, setSuccess] = useState(false);

  const simulateLoad = (setFn: (v: boolean) => void, ms = 2000) => {
    setFn(true);
    setTimeout(() => setFn(false), ms);
  };

  const simulateSuccess = () => {
    setLoading2(true);
    setTimeout(() => {
      setLoading2(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 1500);
    }, 1500);
  };

  return (
    <div className="space-y-4">
      <SubLabel>Button — loading states (click to test)</SubLabel>
      <div className="flex flex-wrap items-center gap-3">
        <Button
          disabled={loading1}
          onClick={() => simulateLoad(setLoading1)}
        >
          {loading1 ? (
            <>
              <Loader2 className="animate-spin" /> Sending...
            </>
          ) : (
            <>
              <ArrowUp /> Send Message
            </>
          )}
        </Button>

        <Button
          variant="interactive"
          disabled={loading2 || success}
          onClick={simulateSuccess}
        >
          {loading2 ? (
            <>
              <Loader2 className="animate-spin" /> Processing...
            </>
          ) : success ? (
            <>
              <Check /> Done
            </>
          ) : (
            <>
              <Upload /> Upload
            </>
          )}
        </Button>

        <Button variant="outline" disabled>
          <Loader2 className="animate-spin" /> Loading...
        </Button>

        <Button size="icon" disabled>
          <Loader2 className="animate-spin" />
        </Button>
      </div>
    </div>
  );
}

// ─── Tooltips ─────────────────────────────────────────────────────────────────

function TooltipShowcase() {
  return (
    <div className="space-y-4">
      <SubLabel>Tooltip — on buttons</SubLabel>
      <div className="flex flex-wrap items-center gap-3">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="icon" variant="outline">
              <Copy />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Copy to clipboard</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="icon" variant="outline">
              <Download />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Download PDF</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button size="icon" variant="outline">
              <Settings />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Settings</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="interactive" size="sm">
              <Scale /> Analyse
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            Run AI-powered legal analysis on this document
          </TooltipContent>
        </Tooltip>
      </div>

      <SubLabel>Tooltip — on inline text</SubLabel>
      <div className="text-sm text-foreground max-w-xl leading-relaxed">
        This contract was reviewed under{' '}
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="text-interactive underline underline-offset-4 decoration-interactive/30 cursor-help">
              Australian Consumer Law
            </span>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="max-w-xs">
            <span className="font-medium">Schedule 2 — Competition and Consumer Act 2010</span>
            <span className="block text-xs text-muted-foreground mt-1">
              Federal legislation governing consumer rights, product safety,
              and unfair business practices across all Australian states and territories.
            </span>
          </TooltipContent>
        </Tooltip>{' '}
        and applies to transactions within the{' '}
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="text-interactive underline underline-offset-4 decoration-interactive/30 cursor-help">
              Federal Court
            </span>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            Federal Court of Australia — original jurisdiction
          </TooltipContent>
        </Tooltip>{' '}
        jurisdiction.
      </div>
    </div>
  );
}

// ─── Badges ───────────────────────────────────────────────────────────────────

function BadgeShowcase() {
  return (
    <div className="space-y-4">
      <SubLabel>Badge — variants</SubLabel>
      <div className="flex flex-wrap gap-2">
        <Badge variant="default">Default</Badge>
        <Badge variant="secondary">Secondary</Badge>
        <Badge variant="outline">Outline</Badge>
        <Badge variant="destructive">Destructive</Badge>
      </div>
    </div>
  );
}

// ─── Inputs ───────────────────────────────────────────────────────────────────

function InputShowcase() {
  const [value, setValue] = useState('');

  return (
    <div className="space-y-4">
      <SubLabel>Input + Label</SubLabel>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl">
        <div className="space-y-2">
          <Label htmlFor="sb-email">Email address</Label>
          <Input
            id="sb-email"
            type="email"
            placeholder="you@example.com"
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sb-disabled">Disabled</Label>
          <Input
            id="sb-disabled"
            type="text"
            placeholder="Not editable"
            disabled
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sb-password">Password</Label>
          <Input id="sb-password" type="password" placeholder="••••••••" />
        </div>
        <div className="space-y-2">
          <Label htmlFor="sb-search">Search</Label>
          <Input id="sb-search" type="search" placeholder="Search..." />
        </div>
      </div>
    </div>
  );
}

// ─── Cards ────────────────────────────────────────────────────────────────────

function CardShowcase() {
  return (
    <div className="space-y-4">
      <SubLabel>Card</SubLabel>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Contract Analysis</CardTitle>
            <CardDescription>
              AI-powered review of legal documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Upload a contract and get instant risk analysis, clause
              identification, and plain-language explanations.
            </p>
          </CardContent>
        </Card>

        <Card className="border-interactive/40 bg-interactive/5">
          <CardHeader>
            <CardTitle>Enterprise Plan</CardTitle>
            <CardDescription>Unlimited legal intelligence</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Full access to all jurisdictions, unlimited queries, and
              priority support.
            </p>
            <Button variant="interactive" size="sm">
              Get started
            </Button>
          </CardContent>
        </Card>

        <InteractiveCardNav
          title="Case Law Research"
          description="Search across 500,000+ Australian cases with AI-powered relevance ranking."
          icon={Scale}
        />

        <InteractiveCardFeature
          title="Multi-Jurisdiction"
          description="Federal, State, and Territory coverage — automatically matched to your query context."
          icon={Globe}
          tag="Coverage"
        />

        <Card className="border-destructive/40 bg-destructive/5">
          <CardHeader>
            <CardTitle className="text-destructive">Access Denied</CardTitle>
            <CardDescription>Your account has been suspended</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Contact support to resolve this issue.
            </p>
          </CardContent>
        </Card>

        <Card className="bg-muted/50">
          <CardHeader>
            <CardTitle>Muted Surface</CardTitle>
            <CardDescription>Secondary information card</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Used for secondary content, tips, or contextual information
              that supports the main content.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ─── Interactive Card — Navigation ────────────────────────────────────────────

function InteractiveCardNav({
  title,
  description,
  icon: Icon,
}: {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card className="group cursor-pointer transition-all hover:border-interactive/40 hover:shadow-sm">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="h-9 w-9 rounded-md bg-interactive/10 flex items-center justify-center">
            <Icon className="h-4 w-4 text-interactive" />
          </div>
          <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-interactive" />
        </div>
        <CardTitle className="text-base pt-2">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}

// ─── Interactive Card — Feature highlight ─────────────────────────────────────

function InteractiveCardFeature({
  title,
  description,
  icon: Icon,
  tag,
}: {
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  tag: string;
}) {
  return (
    <Card className="group cursor-pointer transition-all border-l-2 border-l-interactive/60 hover:border-interactive/40 hover:shadow-sm">
      <CardHeader>
        <div className="flex items-center gap-3">
          <Icon className="h-4 w-4 text-interactive shrink-0" />
          <CardTitle className="text-base">{title}</CardTitle>
          <Badge variant="secondary" className="ml-auto text-[10px]">
            {tag}
          </Badge>
        </div>
        <CardDescription className="pl-7">{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}

// ─── Shared ───────────────────────────────────────────────────────────────────

function SubLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
      {children}
    </p>
  );
}