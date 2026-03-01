# Chain of Thought
A collapsible component that visualizes AI reasoning steps with support for search results, images, and step-by-step progress indicators.
The `ChainOfThought` component provides a visual representation of an AI's reasoning process, showing step-by-step thinking with support for search results, images, and progress indicators. It helps users understand how AI arrives at conclusions.
PreviewCode
Chain of Thought
Searching for profiles for Hayden Bleasel
www.x.comwww.instagram.comwww.github.com
Found the profile photo for Hayden Bleasel
![Example generated image](https://elements.ai-sdk.dev/components/chain-of-thought)
Hayden Bleasel's profile photo from x.com, showing a Ghibli-style man.
Hayden Bleasel is an Australian product designer, software engineer, and founder. He is currently based in the United States working for Vercel, an American cloud application company.
Searching for recent work...
www.github.comwww.dribbble.com
## [Installation](https://elements.ai-sdk.dev/components/chain-of-thought#installation)
AI Elementsshadcn CLIManual
```
npx ai-elements@latest add chain-of-thought
```

## [Features](https://elements.ai-sdk.dev/components/chain-of-thought#features)
  * Collapsible interface with smooth animations powered by Radix UI
  * Step-by-step visualization of AI reasoning process
  * Support for different step statuses (complete, active, pending)
  * Built-in search results display with badge styling
  * Image support with captions for visual content
  * Custom icons for different step types
  * Context-aware components using React Context API
  * Fully typed with TypeScript
  * Accessible with keyboard navigation support
  * Responsive design that adapts to different screen sizes
  * Smooth fade and slide animations for content transitions
  * Composable architecture for flexible customization

## [Props](https://elements.ai-sdk.dev/components/chain-of-thought#props)
### [`<ChainOfThought />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthought-)
Prop
Type
`open?`boolean
`defaultOpen?`boolean
`onOpenChange?`(open: boolean) => void
`...props?`React.ComponentProps<"div">
### [`<ChainOfThoughtHeader />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtheader-)
Prop
Type
`children?`React.ReactNode
`...props?`React.ComponentProps<typeof CollapsibleTrigger>
### [`<ChainOfThoughtStep />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtstep-)
Prop
Type
`icon?`LucideIcon
`label?`string
`description?`string
`status?`"complete" | "active" | "pending"
`...props?`React.ComponentProps<"div">
### [`<ChainOfThoughtSearchResults />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtsearchresults-)
Prop
Type
`...props?`React.ComponentProps<"div">
### [`<ChainOfThoughtSearchResult />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtsearchresult-)
Prop
Type
`...props?`React.ComponentProps<typeof Badge>
### [`<ChainOfThoughtContent />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtcontent-)
Prop
Type
`...props?`React.ComponentProps<typeof CollapsibleContent>
### [`<ChainOfThoughtImage />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtimage-)
Prop
Type
`caption?`string
`...props?`React.ComponentProps<"div">
[AttachmentsA flexible, composable attachment component for displaying files, images, videos, audio, and source documents.](https://elements.ai-sdk.dev/components/attachments)[CheckpointA simple component for marking conversation history points and restoring the chat to a previous state.](https://elements.ai-sdk.dev/components/checkpoint)
### On this page
[Installation](https://elements.ai-sdk.dev/components/chain-of-thought#installation)[Features](https://elements.ai-sdk.dev/components/chain-of-thought#features)[Props](https://elements.ai-sdk.dev/components/chain-of-thought#props)[`<ChainOfThought />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthought-)[`<ChainOfThoughtHeader />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtheader-)[`<ChainOfThoughtStep />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtstep-)[`<ChainOfThoughtSearchResults />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtsearchresults-)[`<ChainOfThoughtSearchResult />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtsearchresult-)[`<ChainOfThoughtContent />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtcontent-)[`<ChainOfThoughtImage />`](https://elements.ai-sdk.dev/components/chain-of-thought#chainofthoughtimage-)
[GitHubEdit this page on GitHub](https://github.com/vercel/ai-elements/edit/main/apps/docs/content/docs/\(chatbot\)/chain-of-thought.mdx)Scroll to topGive feedbackCopy pageAsk AI about this pageOpen in chat
## Chat
What is AI Elements?What can I build with AI Elements?How do I install AI Elements?How do I use AI Elements?
Tip: You can open and close chat with ``⌘``I``
0 / 1000
