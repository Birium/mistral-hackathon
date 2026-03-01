'use client';

/**
 * Loader Showcase — Sandbox Section
 *
 * Interactive demo of a config-driven Chain of Thought loader.
 * Steps progress automatically based on duration config.
 *
 * - Collapsible starts closed — user opens it manually if desired
 * - Header icon changes with each active step
 * - Header icon switches to completedIcon (Brain) when done
 * - Header text shimmers while running, plain text when complete
 * - Jurisdiction switcher (AU / UK / US) resets and reloads the config
 * - Minimal Shimmer primitive examples below
 */

import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import type { LucideIcon } from 'lucide-react';
import { Play, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Shimmer } from '@/components/ai-elements/shimmer';
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '@/components/ai-elements/chain-of-thought';
import { cn } from '@/lib/utils';
import { SubLabel } from './sub-label';
import { ALL_CONFIGS, type LoaderConfig } from './ai-loader-config';

// ─────────────────────────────────────────────────────────────────────────────
// Hook — useLoaderSequence
// ─────────────────────────────────────────────────────────────────────────────

interface LoaderSequenceState {
  stepStatuses: ('pending' | 'active' | 'complete')[];
  headerText: string;
  isRunning: boolean;
  isComplete: boolean;
  isIdle: boolean;
  currentStepIndex: number | null;
  start: () => void;
  reset: () => void;
}

function useLoaderSequence(config: LoaderConfig): LoaderSequenceState {
  const [currentStepIndex, setCurrentStepIndex] = useState<number | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isIdle = currentStepIndex === null && !isComplete;
  const isRunning = currentStepIndex !== null && !isComplete;

  // ── Timer cleanup ──────────────────────────────────────────────────────────
  const clearTimer = useCallback(() => {
    if (timerRef.current !== null) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // ── Auto-progress through steps ───────────────────────────────────────────
  useEffect(() => {
    if (currentStepIndex === null || isComplete) return;

    const step = config.steps[currentStepIndex];
    if (!step) return;

    timerRef.current = setTimeout(() => {
      const nextIndex = currentStepIndex + 1;
      if (nextIndex < config.steps.length) {
        setCurrentStepIndex(nextIndex);
      } else {
        // Last step finished — mark complete
        setIsComplete(true);
      }
    }, step.duration);

    return clearTimer;
  }, [currentStepIndex, isComplete, config.steps, clearTimer]);

  // ── Cleanup on unmount ─────────────────────────────────────────────────────
  useEffect(() => clearTimer, [clearTimer]);

  // ── Derived: step statuses ─────────────────────────────────────────────────
  const stepStatuses = useMemo(() => {
    return config.steps.map((_, i): 'pending' | 'active' | 'complete' => {
      if (isComplete) return 'complete';
      if (currentStepIndex === null) return 'pending';
      if (i < currentStepIndex) return 'complete';
      if (i === currentStepIndex) return 'active';
      return 'pending';
    });
  }, [config.steps, currentStepIndex, isComplete]);

  // ── Derived: header text ───────────────────────────────────────────────────
  const headerText = useMemo(() => {
    if (isComplete) return config.completedHeader;
    if (currentStepIndex !== null) return config.steps[currentStepIndex].headerText;
    return config.steps[0].headerText;
  }, [config, currentStepIndex, isComplete]);

  // ── Controls ───────────────────────────────────────────────────────────────
  const start = useCallback(() => {
    clearTimer();
    setIsComplete(false);
    setCurrentStepIndex(0);
  }, [clearTimer]);

  const reset = useCallback(() => {
    clearTimer();
    setIsComplete(false);
    setCurrentStepIndex(null);
  }, [clearTimer]);

  return {
    stepStatuses,
    headerText,
    isRunning,
    isComplete,
    isIdle,
    currentStepIndex,
    start,
    reset,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Component — LoaderShowcase
// ─────────────────────────────────────────────────────────────────────────────

export function LoaderShowcase() {
  const [selectedConfig, setSelectedConfig] = useState<LoaderConfig>(ALL_CONFIGS[0]);
  // Collapsible starts closed — user opens it manually
  const [isOpen, setIsOpen] = useState(false);

  const loader = useLoaderSequence(selectedConfig);

  // ── Derived: header icon ───────────────────────────────────────────────────
  // complete → config.completedIcon (Brain)
  // running  → current step's icon
  // idle     → undefined (ChainOfThoughtHeader falls back to BrainIcon)
  const currentIcon = useMemo((): LucideIcon | undefined => {
    if (loader.isComplete) return selectedConfig.completedIcon;
    if (loader.currentStepIndex !== null) {
      return selectedConfig.steps[loader.currentStepIndex].icon;
    }
    return undefined;
  }, [loader.isComplete, loader.currentStepIndex, selectedConfig]);

  // ── Handlers ───────────────────────────────────────────────────────────────
  const handleJurisdictionChange = (config: LoaderConfig) => {
    loader.reset();
    setSelectedConfig(config);
    setIsOpen(false);
  };

  const handleStart = () => {
    // Start the sequence but leave the collapsible closed —
    // the user can open it if they want to inspect the steps
    loader.start();
  };

  const handleReset = () => {
    loader.reset();
    setIsOpen(false);
  };

  return (
    <div className="space-y-10">
      {/* ── Interactive Loader Demo ──────────────────────────────────────── */}
      <SubLabel>Loader — config-driven Chain of Thought</SubLabel>

      <div className="flex flex-wrap items-center gap-4">
        {/* Jurisdiction selector — segmented control */}
        <div className="flex items-center gap-0.5 rounded-md border border-border bg-muted/40 p-0.5">
          {ALL_CONFIGS.map((config) => (
            <button
              key={config.label}
              onClick={() => handleJurisdictionChange(config)}
              className={cn(
                'px-3 py-1 rounded text-xs transition-all',
                selectedConfig.label === config.label
                  ? 'bg-background text-foreground shadow-sm font-medium'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {config.label}
            </button>
          ))}
        </div>

        {/* Run / Run again / Reset */}
        {loader.isRunning ? (
          <Button size="sm" variant="outline" onClick={handleReset}>
            <RotateCcw size={14} />
            Reset
          </Button>
        ) : (
          <Button size="sm" variant="interactive" onClick={handleStart}>
            <Play size={14} />
            {loader.isComplete ? 'Run again' : 'Run loader'}
          </Button>
        )}
      </div>

      {/* Chain of Thought — only rendered once started */}
      {!loader.isIdle && (
        <div className="max-w-2xl">
          <ChainOfThought open={isOpen} onOpenChange={setIsOpen}>
            <ChainOfThoughtHeader icon={currentIcon}>
              {loader.isRunning ? (
                // Shimmer wraps the header text while running
                <Shimmer as="span" duration={1.5}>
                  {loader.headerText}
                </Shimmer>
              ) : (
                // Plain text once complete — no shimmer
                loader.headerText
              )}
            </ChainOfThoughtHeader>

            <ChainOfThoughtContent>
              {selectedConfig.steps.map((step, i) => {
                // Progressive reveal: only render steps up to the current one
                if (
                  !loader.isComplete &&
                  loader.currentStepIndex !== null &&
                  i > loader.currentStepIndex
                ) {
                  return null;
                }

                return (
                  <ChainOfThoughtStep
                    key={`${selectedConfig.label}-${i}`}
                    icon={step.icon}
                    label={step.label}
                    description={step.description}
                    status={loader.stepStatuses[i]}
                  >
                    {/* Source badges — shown once step is no longer pending */}
                    {step.searchResults &&
                      loader.stepStatuses[i] !== 'pending' && (
                        <ChainOfThoughtSearchResults>
                          {step.searchResults.map((result) => (
                            <ChainOfThoughtSearchResult key={result}>
                              {result}
                            </ChainOfThoughtSearchResult>
                          ))}
                        </ChainOfThoughtSearchResults>
                      )}
                  </ChainOfThoughtStep>
                );
              })}
            </ChainOfThoughtContent>
          </ChainOfThought>
        </div>
      )}

      {/* ── Shimmer Primitives ───────────────────────────────────────────── */}
      <SubLabel>Shimmer — text animation primitives</SubLabel>
      <div className="space-y-2 max-w-2xl">
        <Shimmer duration={2}>
          Analysing employment contract clauses...
        </Shimmer>
        <Shimmer as="span" duration={3} className="text-sm">
          Cross-referencing Federal Court judgments...
        </Shimmer>
      </div>
    </div>
  );
}