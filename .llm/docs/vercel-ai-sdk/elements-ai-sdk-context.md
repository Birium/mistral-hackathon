# Context
A compound component system for displaying AI model context window usage, token consumption, and cost estimation.
The `Context` component provides a comprehensive view of AI model usage through a compound component system. It displays context window utilization, token consumption breakdown (input, output, reasoning, cache), and cost estimation in an interactive hover card interface.
PreviewCode
31.3%
## [Installation](https://elements.ai-sdk.dev/components/context#installation)
AI Elementsshadcn CLIManual
```
npx ai-elements@latest add context
```

## [Features](https://elements.ai-sdk.dev/components/context#features)
  * **Compound Component Architecture** : Flexible composition of context display elements
  * **Visual Progress Indicator** : Circular SVG progress ring showing context usage percentage
  * **Token Breakdown** : Detailed view of input, output, reasoning, and cached tokens
  * **Cost Estimation** : Real-time cost calculation using the `tokenlens` library
  * **Intelligent Formatting** : Automatic token count formatting (K, M, B suffixes)
  * **Interactive Hover Card** : Detailed information revealed on hover
  * **Context Provider Pattern** : Clean data flow through React Context API
  * **TypeScript Support** : Full type definitions for all components
  * **Accessible Design** : Proper ARIA labels and semantic HTML
  * **Theme Integration** : Uses currentColor for automatic theme adaptation

## [Props](https://elements.ai-sdk.dev/components/context#props)
### [`<Context />`](https://elements.ai-sdk.dev/components/context#context-)
Prop
Type
`maxTokens?`number
`usedTokens?`number
`usage?`LanguageModelUsage
`modelId?`ModelId
`...props?`ComponentProps<HoverCard>
### [`<ContextTrigger />`](https://elements.ai-sdk.dev/components/context#contexttrigger-)
Prop
Type
`children?`React.ReactNode
`...props?`ComponentProps<Button>
### [`<ContextContent />`](https://elements.ai-sdk.dev/components/context#contextcontent-)
Prop
Type
`className?`string
`...props?`ComponentProps<HoverCardContent>
### [`<ContextContentHeader />`](https://elements.ai-sdk.dev/components/context#contextcontentheader-)
Prop
Type
`children?`React.ReactNode
`...props?`ComponentProps<div>
### [`<ContextContentBody />`](https://elements.ai-sdk.dev/components/context#contextcontentbody-)
Prop
Type
`children?`React.ReactNode
`...props?`ComponentProps<div>
### [`<ContextContentFooter />`](https://elements.ai-sdk.dev/components/context#contextcontentfooter-)
Prop
Type
`children?`React.ReactNode
`...props?`ComponentProps<div>
### [Usage Components](https://elements.ai-sdk.dev/components/context#usage-components)
All usage components (`ContextInputUsage`, `ContextOutputUsage`, `ContextReasoningUsage`, `ContextCacheUsage`) share the same props:
Prop
Type
`children?`React.ReactNode
`className?`string
`...props?`ComponentProps<div>
## [Component Architecture](https://elements.ai-sdk.dev/components/context#component-architecture)
The Context component uses a compound component pattern with React Context for data sharing:
  1. **`<Context>`**- Root provider component that holds all context data
  2. **`<ContextTrigger>`**- Interactive trigger element (default: button with percentage)
  3. **`<ContextContent>`**- Hover card content container
  4. **`<ContextContentHeader>`**- Header section with progress visualization
  5. **`<ContextContentBody>`**- Body section for usage breakdowns
  6. **`<ContextContentFooter>`**- Footer section for total cost
  7. **Usage Components** - Individual token usage displays (Input, Output, Reasoning, Cache)

## [Token Formatting](https://elements.ai-sdk.dev/components/context#token-formatting)
The component uses `Intl.NumberFormat` with compact notation for automatic formatting:
  * Under 1,000: Shows exact count (e.g., "842")
  * 1,000+: Shows with K suffix (e.g., "32K")
  * 1,000,000+: Shows with M suffix (e.g., "1.5M")
  * 1,000,000,000+: Shows with B suffix (e.g., "2.1B")

## [Cost Calculation](https://elements.ai-sdk.dev/components/context#cost-calculation)
When a `modelId` is provided, the component automatically calculates costs using the `tokenlens` library:
  * **Input tokens** : Cost based on model's input pricing
  * **Output tokens** : Cost based on model's output pricing
  * **Reasoning tokens** : Special pricing for reasoning-capable models
  * **Cached tokens** : Reduced pricing for cached input tokens
  * **Total cost** : Sum of all token type costs

Costs are formatted using `Intl.NumberFormat` with USD currency.
## [Styling](https://elements.ai-sdk.dev/components/context#styling)
The component uses Tailwind CSS classes and follows your design system:
  * Progress indicator uses `currentColor` for theme adaptation
  * Hover card has customizable width and padding
  * Footer has a secondary background for visual separation
  * All text sizes use the `text-xs` class for consistency
  * Muted foreground colors for secondary information

[ConfirmationAn alert-based component for managing tool execution approval workflows with request, accept, and reject states.](https://elements.ai-sdk.dev/components/confirmation)[ConversationWraps messages and automatically scrolls to the bottom. Also includes a scroll button that appears when not at the bottom.](https://elements.ai-sdk.dev/components/conversation)
### On this page
[Installation](https://elements.ai-sdk.dev/components/context#installation)[Features](https://elements.ai-sdk.dev/components/context#features)[Props](https://elements.ai-sdk.dev/components/context#props)[`<Context />`](https://elements.ai-sdk.dev/components/context#context-)[`<ContextTrigger />`](https://elements.ai-sdk.dev/components/context#contexttrigger-)[`<ContextContent />`](https://elements.ai-sdk.dev/components/context#contextcontent-)[`<ContextContentHeader />`](https://elements.ai-sdk.dev/components/context#contextcontentheader-)[`<ContextContentBody />`](https://elements.ai-sdk.dev/components/context#contextcontentbody-)[`<ContextContentFooter />`](https://elements.ai-sdk.dev/components/context#contextcontentfooter-)[Usage Components](https://elements.ai-sdk.dev/components/context#usage-components)[Component Architecture](https://elements.ai-sdk.dev/components/context#component-architecture)[Token Formatting](https://elements.ai-sdk.dev/components/context#token-formatting)[Cost Calculation](https://elements.ai-sdk.dev/components/context#cost-calculation)[Styling](https://elements.ai-sdk.dev/components/context#styling)
[GitHubEdit this page on GitHub](https://github.com/vercel/ai-elements/edit/main/apps/docs/content/docs/\(chatbot\)/context.mdx)Scroll to topGive feedbackCopy pageAsk AI about this pageOpen in chat
## Chat
What is AI Elements?What can I build with AI Elements?How do I install AI Elements?How do I use AI Elements?
Tip: You can open and close chat with ``⌘``I``
0 / 1000
