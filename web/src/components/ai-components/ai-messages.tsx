'use client';

import {
  Message,
  MessageAction,
  MessageActions,
  MessageContent,
  MessageResponse,
} from '@/components/ai-elements/message';
import { Copy, RefreshCcw } from 'lucide-react';
import { SubLabel } from './sub-label';

// ─────────────────────────────────────────────────────────────────────────────
// Mock Data
// ─────────────────────────────────────────────────────────────────────────────

// Clean markdown — headings, bullet list, blockquote only (no code blocks)
const MOCK_LEGAL_RESPONSE = `
Under **Schedule 2** of the *Competition and Consumer Act 2010* (Cth), the following obligations apply automatically to all businesses operating in Australia.

### Consumer Guarantees

Goods and services supplied to consumers carry automatic guarantees:

- **Acceptable quality** — safe, durable, free from defects, and fit for purpose
- **Fit for disclosed purpose** — suitable for any specific purpose made known to the supplier
- **Matching description** — goods must correspond to any description provided
- **Repairs and spare parts** — availability must be ensured for a reasonable period

> **Important:** These guarantees cannot be excluded, restricted, or modified by contract. Any term attempting to do so is void under s64 ACL.
`.trim();

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export function MessagesShowcase() {
  return (
    <div className="space-y-6">
      <SubLabel>Messages — conversation thread with markdown</SubLabel>
      <div className="max-w-2xl space-y-2">
        {/* User message */}
        <Message from="user">
          <MessageContent>
            <p>What are the key requirements under the Australian Consumer Law?</p>
          </MessageContent>
        </Message>

        {/* Assistant message — markdown rendered via Streamdown */}
        <Message from="assistant">
          <MessageContent>
            <MessageResponse>{MOCK_LEGAL_RESPONSE}</MessageResponse>
          </MessageContent>
          <MessageActions>
            <MessageAction label="Copy" onClick={() => {}}>
              <Copy className="size-3" />
            </MessageAction>
            <MessageAction label="Retry" onClick={() => {}}>
              <RefreshCcw className="size-3" />
            </MessageAction>
          </MessageActions>
        </Message>
      </div>
    </div>
  );
}