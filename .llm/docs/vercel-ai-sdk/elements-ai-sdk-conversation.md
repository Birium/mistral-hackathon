# Conversation
Wraps messages and automatically scrolls to the bottom. Also includes a scroll button that appears when not at the bottom.
The `Conversation` component wraps messages and automatically scrolls to the bottom. Also includes a scroll button that appears when not at the bottom.
PreviewCode
Hello, how are you?
## [Installation](https://elements.ai-sdk.dev/components/conversation#installation)
AI Elementsshadcn CLIManual
```
npx ai-elements@latest add conversation
```

## [Usage with AI SDK](https://elements.ai-sdk.dev/components/conversation#usage-with-ai-sdk)
Build a simple conversational UI with `Conversation` and [`PromptInput`](https://elements.ai-sdk.dev/components/prompt-input):
Add the following component to your frontend:
app/page.tsx
```
"use client";
import {
 Conversation,
 ConversationContent,
 ConversationDownload,
 ConversationEmptyState,
 ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
 Message,
 MessageContent,
 MessageResponse,
} from "@/components/ai-elements/message";
import {
 Input,
 PromptInputTextarea,
 PromptInputSubmit,
} from "@/components/ai-elements/prompt-input";
import { MessageSquare } from "lucide-react";
import { useState } from "react";
import { useChat } from "@ai-sdk/react";
const ConversationDemo = () => {
 const [input, setInput] = useState("");
 const { messages, sendMessage, status } = useChat();
 const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  if (input.trim()) {
   sendMessage({ text: input });
   setInput("");
  }
 };
 return (
  <div className="max-w-4xl mx-auto p-6 relative size-full rounded-lg border h-[600px]">
   <div className="flex flex-col h-full">
    <Conversation>
     <ConversationContent>
      {messages.length === 0 ? (
       <ConversationEmptyState
        icon={<MessageSquare className="size-12" />}
        title="Start a conversation"
        description="Type a message below to begin chatting"
       />
      ) : (
       messages.map((message) => (
        <Message from={message.role} key={message.id}>
         <MessageContent>
          {message.parts.map((part, i) => {
           switch (part.type) {
            case "text": // we don't use any reasoning or tool calls in this example
             return (
              <MessageResponse key={`${message.id}-${i}`}>
               {part.text}
              </MessageResponse>
             );
            default:
             return null;
           }
          })}
         </MessageContent>
        </Message>
       ))
      )}
     </ConversationContent>
     <ConversationDownload messages={messages} />
     <ConversationScrollButton />
    </Conversation>
    <Input
     onSubmit={handleSubmit}
     className="mt-4 w-full max-w-2xl mx-auto relative"
    >
     <PromptInputTextarea
      value={input}
      placeholder="Say something..."
      onChange={(e) => setInput(e.currentTarget.value)}
      className="pr-12"
     />
     <PromptInputSubmit
      status={status === "streaming" ? "streaming" : "ready"}
      disabled={!input.trim()}
      className="absolute bottom-1 right-1"
     />
    </Input>
   </div>
  </div>
 );
};
export default ConversationDemo;
```

Add the following route to your backend:
api/chat/route.ts
```
import { streamText, UIMessage, convertToModelMessages } from "ai";
// Allow streaming responses up to 30 seconds
export const maxDuration = 30;
export async function POST(req: Request) {
 const { messages }: { messages: UIMessage[] } = await req.json();
 const result = streamText({
  model: "openai/gpt-4o",
  messages: await convertToModelMessages(messages),
 });
 return result.toUIMessageStreamResponse();
}
```

## [Features](https://elements.ai-sdk.dev/components/conversation#features)
  * Automatic scrolling to the bottom when new messages are added
  * Smooth scrolling behavior with configurable animation
  * Scroll button that appears when not at the bottom
  * Download conversation as Markdown
  * Responsive design with customizable padding and spacing
  * Flexible content layout with consistent message spacing
  * Accessible with proper ARIA roles for screen readers
  * Customizable styling through className prop
  * Support for any number of child message components

## [Props](https://elements.ai-sdk.dev/components/conversation#props)
### [`<Conversation />`](https://elements.ai-sdk.dev/components/conversation#conversation-)
Prop
Type
`contextRef?`React.Ref<StickToBottomContext>
`instance?`StickToBottomInstance
`children?`((context: StickToBottomContext) => ReactNode) | ReactNode
`...props?`Omit<React.HTMLAttributes<HTMLDivElement>, "children">
### [`<ConversationContent />`](https://elements.ai-sdk.dev/components/conversation#conversationcontent-)
Prop
Type
`children?`((context: StickToBottomContext) => ReactNode) | ReactNode
`...props?`Omit<React.HTMLAttributes<HTMLDivElement>, "children">
### [`<ConversationEmptyState />`](https://elements.ai-sdk.dev/components/conversation#conversationemptystate-)
Prop
Type
`title?`string
`description?`string
`icon?`React.ReactNode
`children?`React.ReactNode
`...props?`ComponentProps<"div">
### [`<ConversationScrollButton />`](https://elements.ai-sdk.dev/components/conversation#conversationscrollbutton-)
Prop
Type
`...props?`ComponentProps<typeof Button>
### [`<ConversationDownload />`](https://elements.ai-sdk.dev/components/conversation#conversationdownload-)
A button that downloads the conversation as a Markdown file.
```
import { ConversationDownload } from "@/components/ai-elements/conversation";
<Conversation>
 <ConversationContent>
  {messages.map(...)}
 </ConversationContent>
 <ConversationDownload messages={messages} />
 <ConversationScrollButton />
</Conversation>
```

Prop
Type
`messages`ConversationMessage[]
`filename?`string
`formatMessage?`(message: ConversationMessage, index: number) => string
`...props?`Omit<ComponentProps<typeof Button>, 'onClick'>
### [`messagesToMarkdown`](https://elements.ai-sdk.dev/components/conversation#messagestomarkdown)
A utility function to convert messages to Markdown format. Useful for custom download implementations.
```
import { messagesToMarkdown } from "@/components/ai-elements/conversation";
const markdown = messagesToMarkdown(messages);
// With custom formatter
const customMarkdown = messagesToMarkdown(
 messages,
 (msg, i) => `[${msg.role}]: ${msg.content}`
);
```

[ContextA compound component system for displaying AI model context window usage, token consumption, and cost estimation.](https://elements.ai-sdk.dev/components/context)[Inline CitationA hoverable citation component that displays source information and quotes inline with text, perfect for AI-generated content with references.](https://elements.ai-sdk.dev/components/inline-citation)
### On this page
[Installation](https://elements.ai-sdk.dev/components/conversation#installation)[Usage with AI SDK](https://elements.ai-sdk.dev/components/conversation#usage-with-ai-sdk)[Features](https://elements.ai-sdk.dev/components/conversation#features)[Props](https://elements.ai-sdk.dev/components/conversation#props)[`<Conversation />`](https://elements.ai-sdk.dev/components/conversation#conversation-)[`<ConversationContent />`](https://elements.ai-sdk.dev/components/conversation#conversationcontent-)[`<ConversationEmptyState />`](https://elements.ai-sdk.dev/components/conversation#conversationemptystate-)[`<ConversationScrollButton />`](https://elements.ai-sdk.dev/components/conversation#conversationscrollbutton-)[`<ConversationDownload />`](https://elements.ai-sdk.dev/components/conversation#conversationdownload-)[`messagesToMarkdown`](https://elements.ai-sdk.dev/components/conversation#messagestomarkdown)
[GitHubEdit this page on GitHub](https://github.com/vercel/ai-elements/edit/main/apps/docs/content/docs/\(chatbot\)/conversation.mdx)Scroll to topGive feedbackCopy pageAsk AI about this pageOpen in chat
## Chat
What is AI Elements?What can I build with AI Elements?How do I install AI Elements?How do I use AI Elements?
Tip: You can open and close chat with ``⌘``I``
0 / 1000
