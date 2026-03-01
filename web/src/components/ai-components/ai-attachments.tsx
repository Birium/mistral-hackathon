'use client';

import {
  Attachment,
  AttachmentInfo,
  AttachmentPreview,
  AttachmentRemove,
  Attachments,
} from '@/components/ai-elements/attachments';
import { SubLabel } from './sub-label';

// ─────────────────────────────────────────────────────────────────────────────
// Mock Data
// ─────────────────────────────────────────────────────────────────────────────

// Image files — used for grid variant (Unsplash, legal/professional theme)
const MOCK_IMAGE_FILES = [
  {
    id: 'img-1',
    type: 'file' as const,
    filename: 'contract-signing.jpg',
    mediaType: 'image/jpeg',
    url: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&h=400&fit=crop',
  },
  {
    id: 'img-2',
    type: 'file' as const,
    filename: 'legal-documents.jpg',
    mediaType: 'image/jpeg',
    url: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=400&h=400&fit=crop',
  },
  {
    id: 'img-3',
    type: 'file' as const,
    filename: 'courtroom.jpg',
    mediaType: 'image/jpeg',
    url: 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=400&h=400&fit=crop',
  },
];

// Document files — used for inline & list variants
const MOCK_DOC_FILES = [
  {
    id: 'doc-1',
    type: 'file' as const,
    filename: 'employment-contract-2024.pdf',
    mediaType: 'application/pdf',
    url: '#',
  },
  {
    id: 'doc-2',
    type: 'file' as const,
    filename: 'court-order-supreme.pdf',
    mediaType: 'application/pdf',
    url: '#',
  },
  {
    id: 'doc-3',
    type: 'file' as const,
    filename: 'lease-agreement.pdf',
    mediaType: 'application/pdf',
    url: '#',
  },
  {
    id: 'doc-4',
    type: 'file' as const,
    filename: 'nda-confidentiality.pdf',
    mediaType: 'application/pdf',
    url: '#',
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export function AttachmentsShowcase() {
  return (
    <div className="space-y-8">
      <SubLabel>Attachments — grid (images)</SubLabel>
      <Attachments variant="grid">
        {MOCK_IMAGE_FILES.map((file) => (
          <Attachment key={file.id} data={file}>
            <AttachmentPreview />
            <AttachmentInfo />
          </Attachment>
        ))}
      </Attachments>

      <SubLabel>Attachments — inline (documents)</SubLabel>
      <Attachments variant="inline">
        {MOCK_DOC_FILES.map((file) => (
          <Attachment key={file.id} data={file}>
            <AttachmentPreview />
            <AttachmentInfo />
          </Attachment>
        ))}
      </Attachments>

      <SubLabel>Attachments — list (with remove)</SubLabel>
      <Attachments variant="list">
        {MOCK_DOC_FILES.map((file) => (
          <Attachment key={file.id} data={file} onRemove={() => {}}>
            <AttachmentPreview />
            <AttachmentInfo showMediaType />
            <AttachmentRemove />
          </Attachment>
        ))}
      </Attachments>
    </div>
  );
}