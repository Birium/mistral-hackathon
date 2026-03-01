'use client';

import { Shimmer } from '@/components/ai-elements/shimmer';
import { SubLabel } from './sub-label';

export function ShimmerShowcase() {
  return (
    <div className="space-y-10">
      <SubLabel>Shimmer — AI thinking states (duration variants)</SubLabel>

      {/* Card background gives the gradient animation maximum contrast */}
      <div className="bg-card border border-border rounded-lg p-6 space-y-4">
        <Shimmer duration={1}>
          Retrieving case law precedents...
        </Shimmer>
        <Shimmer duration={2}>
          Analysing employment contract clauses...
        </Shimmer>
        <Shimmer duration={4}>
          Cross-referencing Federal Court judgments across all Australian jurisdictions...
        </Shimmer>
      </div>

      <SubLabel>Shimmer — element variants</SubLabel>
      <div className="bg-card border border-border rounded-lg p-6 space-y-4">
        <Shimmer as="h2" className="font-serif text-2xl font-bold">
          Legal Intelligence for Australian Law
        </Shimmer>
        <Shimmer as="p" className="text-sm">
          Supporting text shimmer — secondary loading state for metadata and captions.
        </Shimmer>
        <p className="text-sm text-foreground leading-relaxed">
          The court held that{' '}
          <Shimmer as="span" duration={1.5} className="font-medium">
            this clause constitutes an unfair contract term
          </Shimmer>{' '}
          under s24 of the Australian Consumer Law.
        </p>
      </div>
    </div>
  );
}