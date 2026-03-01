'use client';

import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtSearchResult,
  ChainOfThoughtSearchResults,
  ChainOfThoughtStep,
} from '@/components/ai-elements/chain-of-thought';
import { FileText, Scale, Search } from 'lucide-react';
import { SubLabel } from './sub-label';

export function ChainOfThoughtShowcase() {
  return (
    <div className="space-y-8">
      <SubLabel>Chain of Thought — research in progress (expanded)</SubLabel>
      <div className="max-w-2xl">
        <ChainOfThought defaultOpen>
          <ChainOfThoughtHeader>Analysing your legal question</ChainOfThoughtHeader>
          <ChainOfThoughtContent>
            <ChainOfThoughtStep
              icon={Search}
              label="Parsing query"
              description="Identifying jurisdiction, legislation, and legal concepts."
              status="complete"
            />
            <ChainOfThoughtStep
              icon={Scale}
              label="Searching Australian legal databases"
              status="active"
            >
              <ChainOfThoughtSearchResults>
                <ChainOfThoughtSearchResult>austlii.edu.au</ChainOfThoughtSearchResult>
                <ChainOfThoughtSearchResult>federalcourt.gov.au</ChainOfThoughtSearchResult>
                <ChainOfThoughtSearchResult>legislation.gov.au</ChainOfThoughtSearchResult>
                <ChainOfThoughtSearchResult>hca.gov.au</ChainOfThoughtSearchResult>
              </ChainOfThoughtSearchResults>
            </ChainOfThoughtStep>
            <ChainOfThoughtStep
              icon={FileText}
              label="Drafting structured response"
              description="Synthesising findings into a plain-language legal analysis."
              status="pending"
            />
          </ChainOfThoughtContent>
        </ChainOfThought>
      </div>

      <SubLabel>Chain of Thought — research complete (collapsed by default)</SubLabel>
      <div className="max-w-2xl">
        <ChainOfThought defaultOpen={false}>
          <ChainOfThoughtHeader>Research complete — 4 sources found</ChainOfThoughtHeader>
          <ChainOfThoughtContent>
            <ChainOfThoughtStep
              icon={Search}
              label="Query parsed"
              status="complete"
            />
            <ChainOfThoughtStep
              icon={Scale}
              label="4 relevant cases retrieved"
              status="complete"
            >
              <ChainOfThoughtSearchResults>
                <ChainOfThoughtSearchResult>austlii.edu.au</ChainOfThoughtSearchResult>
                <ChainOfThoughtSearchResult>hca.gov.au</ChainOfThoughtSearchResult>
              </ChainOfThoughtSearchResults>
            </ChainOfThoughtStep>
            <ChainOfThoughtStep
              icon={FileText}
              label="Response drafted"
              status="complete"
            />
          </ChainOfThoughtContent>
        </ChainOfThought>
      </div>
    </div>
  );
}