'use client';

import { useState } from 'react';
import {
  PromptInput,
  PromptInputBody,
  PromptInputButton,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
  PromptInputTools,
  type PromptInputMessage,
} from '@/components/ai-elements/prompt-input';
import { Globe } from 'lucide-react';
import { SubLabel } from './sub-label';

export function PromptInputShowcase() {
  const [value, setValue] = useState('');

  // Static demo — no backend connected
  const handleSubmit = (_message: PromptInputMessage) => {
    setValue('');
  };

  return (
    <div className="space-y-6">
      <SubLabel>Prompt Input — chat input with jurisdiction selector</SubLabel>
      <PromptInput onSubmit={handleSubmit} className="max-w-2xl">
        <PromptInputBody>
          <PromptInputTextarea
            value={value}
            placeholder="Ask about Australian law..."
            onChange={(e) => setValue(e.target.value)}
          />
        </PromptInputBody>
        <PromptInputFooter>
          <PromptInputTools>
            <PromptInputButton
              tooltip={{ content: 'Switch jurisdiction', side: 'top' }}
              variant="ghost"
            >
              <Globe size={16} />
              <span>Australia</span>
            </PromptInputButton>
          </PromptInputTools>
          <PromptInputSubmit status="ready" disabled={!value.trim()} />
        </PromptInputFooter>
      </PromptInput>
    </div>
  );
}