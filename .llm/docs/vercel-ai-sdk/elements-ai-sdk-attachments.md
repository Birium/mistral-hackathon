# Attachments
A flexible, composable attachment component for displaying files, images, videos, audio, and source documents.
The `Attachment` component provides a unified way to display file attachments and source documents with multiple layout variants.
PreviewCode
![mountain-landscape.jpg](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop)
Remove
![ocean-sunset.jpg](https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=400&h=400&fit=crop)
Remove
Remove
Remove
## [Installation](https://elements.ai-sdk.dev/components/attachments#installation)
AI Elementsshadcn CLIManual
```
npx ai-elements@latest add attachments
```

## [Usage with AI SDK](https://elements.ai-sdk.dev/components/attachments#usage-with-ai-sdk)
Display user-uploaded files in chat messages or input areas.
app/page.tsx
```
"use client";
import {
 Attachments,
 Attachment,
 AttachmentPreview,
 AttachmentInfo,
 AttachmentRemove,
} from "@/components/ai-elements/attachments";
import type { FileUIPart } from "ai";
interface MessageProps {
 attachments: (FileUIPart & { id: string })[];
 onRemove?: (id: string) => void;
}
const MessageAttachments = ({ attachments, onRemove }: MessageProps) => (
 <Attachments variant="grid">
  {attachments.map((file) => (
   <Attachment
    key={file.id}
    data={file}
    onRemove={onRemove ? () => onRemove(file.id) : undefined}
   >
    <AttachmentPreview />
    <AttachmentRemove />
   </Attachment>
  ))}
 </Attachments>
);
export default MessageAttachments;
```

## [Features](https://elements.ai-sdk.dev/components/attachments#features)
  * Three display variants: grid (thumbnails), inline (badges), and list (rows)
  * Supports both FileUIPart and SourceDocumentUIPart from the AI SDK
  * Automatic media type detection (image, video, audio, document, source)
  * Hover card support for inline previews
  * Remove button with customizable callback
  * Composable architecture for maximum flexibility
  * Accessible with proper ARIA labels
  * TypeScript support with exported utility functions

## [Examples](https://elements.ai-sdk.dev/components/attachments#examples)
### [Grid Variant](https://elements.ai-sdk.dev/components/attachments#grid-variant)
Best for displaying attachments in messages with visual thumbnails.
PreviewCode
![mountain-landscape.jpg](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop)
Remove
![ocean-sunset.jpg](https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=400&h=400&fit=crop)
Remove
Remove
Remove
### [Inline Variant](https://elements.ai-sdk.dev/components/attachments#inline-variant)
Best for compact badge-style display in input areas with hover previews.
PreviewCode
![mountain-landscape.jpg](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop)
Remove
mountain-landscape.jpg
Remove
quarterly-report.pdf
Remove
React Documentation
Remove
podcast-episode.mp3
### [List Variant](https://elements.ai-sdk.dev/components/attachments#list-variant)
Best for file lists with full metadata display.
PreviewCode
![mountain-landscape.jpg](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=400&fit=crop)
mountain-landscape.jpgimage/jpeg
Remove
quarterly-report-2024.pdfapplication/pdf
Remove
product-demo.mp4video/mp4
Remove
API Documentationtext/html
Remove
meeting-recording.mp3audio/mpeg
Remove
## [Props](https://elements.ai-sdk.dev/components/attachments#props)
### [`<Attachments />`](https://elements.ai-sdk.dev/components/attachments#attachments-)
Container component that sets the layout variant.
Prop
Type
`variant?`"grid" | "inline" | "list"
`...props?`React.HTMLAttributes<HTMLDivElement>
### [`<Attachment />`](https://elements.ai-sdk.dev/components/attachments#attachment-)
Individual attachment item wrapper.
Prop
Type
`data?`(FileUIPart & { id: string }) | (SourceDocumentUIPart & { id: string })
`onRemove?`() => void
`...props?`React.HTMLAttributes<HTMLDivElement>
### [`<AttachmentPreview />`](https://elements.ai-sdk.dev/components/attachments#attachmentpreview-)
Displays the media preview (image, video, or icon).
Prop
Type
`fallbackIcon?`React.ReactNode
`...props?`React.HTMLAttributes<HTMLDivElement>
### [`<AttachmentInfo />`](https://elements.ai-sdk.dev/components/attachments#attachmentinfo-)
Displays the filename and optional media type.
Prop
Type
`showMediaType?`boolean
`...props?`React.HTMLAttributes<HTMLDivElement>
### [`<AttachmentRemove />`](https://elements.ai-sdk.dev/components/attachments#attachmentremove-)
Remove button that appears on hover.
Prop
Type
`label?`string
`...props?`React.ComponentProps<typeof Button>
### [`<AttachmentHoverCard />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercard-)
Wrapper for hover preview functionality.
Prop
Type
`openDelay?`number
`closeDelay?`number
`...props?`React.ComponentProps<typeof HoverCard>
### [`<AttachmentHoverCardTrigger />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercardtrigger-)
Trigger element for the hover card.
Prop
Type
`...props?`React.ComponentProps<typeof HoverCardTrigger>
### [`<AttachmentHoverCardContent />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercardcontent-)
Content displayed in the hover card.
Prop
Type
`align?`"start" | "center" | "end"
`...props?`React.ComponentProps<typeof HoverCardContent>
### [`<AttachmentEmpty />`](https://elements.ai-sdk.dev/components/attachments#attachmentempty-)
Empty state component when no attachments are present.
Prop
Type
`...props?`React.HTMLAttributes<HTMLDivElement>
## [Utility Functions](https://elements.ai-sdk.dev/components/attachments#utility-functions)
### [`getMediaCategory(data)`](https://elements.ai-sdk.dev/components/attachments#getmediacategorydata)
Returns the media category for an attachment.
```
import { getMediaCategory } from "@/components/ai-elements/attachments";
const category = getMediaCategory(attachment);
// Returns: "image" | "video" | "audio" | "document" | "source" | "unknown"
```

### [`getAttachmentLabel(data)`](https://elements.ai-sdk.dev/components/attachments#getattachmentlabeldata)
Returns the display label for an attachment.
```
import { getAttachmentLabel } from "@/components/ai-elements/attachments";
const label = getAttachmentLabel(attachment);
// Returns filename or fallback like "Image" or "Attachment"
```

[Chain of ThoughtA collapsible component that visualizes AI reasoning steps with support for search results, images, and step-by-step progress indicators.](https://elements.ai-sdk.dev/components/chain-of-thought)
### On this page
[Installation](https://elements.ai-sdk.dev/components/attachments#installation)[Usage with AI SDK](https://elements.ai-sdk.dev/components/attachments#usage-with-ai-sdk)[Features](https://elements.ai-sdk.dev/components/attachments#features)[Examples](https://elements.ai-sdk.dev/components/attachments#examples)[Grid Variant](https://elements.ai-sdk.dev/components/attachments#grid-variant)[Inline Variant](https://elements.ai-sdk.dev/components/attachments#inline-variant)[List Variant](https://elements.ai-sdk.dev/components/attachments#list-variant)[Props](https://elements.ai-sdk.dev/components/attachments#props)[`<Attachments />`](https://elements.ai-sdk.dev/components/attachments#attachments-)[`<Attachment />`](https://elements.ai-sdk.dev/components/attachments#attachment-)[`<AttachmentPreview />`](https://elements.ai-sdk.dev/components/attachments#attachmentpreview-)[`<AttachmentInfo />`](https://elements.ai-sdk.dev/components/attachments#attachmentinfo-)[`<AttachmentRemove />`](https://elements.ai-sdk.dev/components/attachments#attachmentremove-)[`<AttachmentHoverCard />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercard-)[`<AttachmentHoverCardTrigger />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercardtrigger-)[`<AttachmentHoverCardContent />`](https://elements.ai-sdk.dev/components/attachments#attachmenthovercardcontent-)[`<AttachmentEmpty />`](https://elements.ai-sdk.dev/components/attachments#attachmentempty-)[Utility Functions](https://elements.ai-sdk.dev/components/attachments#utility-functions)[`getMediaCategory(data)`](https://elements.ai-sdk.dev/components/attachments#getmediacategorydata)[`getAttachmentLabel(data)`](https://elements.ai-sdk.dev/components/attachments#getattachmentlabeldata)
[GitHubEdit this page on GitHub](https://github.com/vercel/ai-elements/edit/main/apps/docs/content/docs/\(chatbot\)/attachments.mdx)Scroll to topGive feedbackCopy pageAsk AI about this pageOpen in chat
## Chat
What is AI Elements?What can I build with AI Elements?How do I install AI Elements?How do I use AI Elements?
Tip: You can open and close chat with ``⌘``I``
0 / 1000
