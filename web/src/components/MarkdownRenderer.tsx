import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { FileLink } from '@/components/shared/FileLink'

interface MarkdownRendererProps {
  content: string
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Returns true if the href points to a vault file rather than an external URL.
 */
function isVaultPath(href: string): boolean {
  if (!href) return false
  if (/^https?:\/\//.test(href)) return false
  if (href.startsWith('mailto:')) return false
  if (href.startsWith('#')) return false
  if (/\.\w{1,5}$/.test(href)) return true
  if (href.includes('/') && !href.startsWith('//')) return true
  return false
}

/**
 * Extracts the language string from a fenced code block's hast AST node.
 * The language is stored as `language-xxx` in the className of the <code> child.
 */
function extractLangFromNode(node: unknown): string | null {
  const el = node as {
    children?: Array<{
      type?: string
      tagName?: string
      properties?: { className?: string[] }
    }>
  }
  const codeChild = el?.children?.[0]
  if (codeChild?.type !== 'element' || codeChild?.tagName !== 'code') return null
  const classNames = codeChild.properties?.className
  if (!Array.isArray(classNames) || classNames.length === 0) return null
  const langClass = classNames.find(
    (c) => typeof c === 'string' && c.startsWith('language-'),
  )
  return langClass ? langClass.replace('language-', '') : null
}

/**
 * Returns true if the lang string looks like a vault file path.
 * Examples: "tasks.md", "projects/freelance-fintech/blockers.md"
 */
function isFileLang(lang: string): boolean {
  return /\.\w{1,5}$/.test(lang)
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-2xl font-bold mt-6 mb-3 text-foreground">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-xl font-semibold mt-5 mb-2 text-foreground">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-lg font-semibold mt-4 mb-2 text-foreground">{children}</h3>
        ),
        p: ({ children }) => (
          <p className="mb-3 leading-relaxed text-foreground">{children}</p>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="text-foreground leading-relaxed">{children}</li>
        ),

        // ── Inline code ──────────────────────────────────────────────────────
        code: ({ children, className }) => (
          <code
            className={
              className
                ? `font-mono text-sm ${className}`
                : 'bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-foreground'
            }
          >
            {children}
          </code>
        ),

        // ── Fenced code blocks ───────────────────────────────────────────────
        // If the language tag is a vault file path (e.g. ```tasks.md),
        // render ONLY a file link — the content is not shown.
        // Regular code blocks render normally.
        pre: ({ children, node }) => {
          const lang = extractLangFromNode(node)
          const isFile = lang ? isFileLang(lang) : false

          if (isFile && lang) {
            return (
              <div className="mb-1">
                <FileLink path={lang} />
              </div>
            )
          }

          return (
            <pre className="bg-muted/50 border rounded-md p-4 overflow-x-auto mb-3 text-sm font-mono leading-relaxed">
              {children}
            </pre>
          )
        },

        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-border pl-4 italic text-muted-foreground mb-3">
            {children}
          </blockquote>
        ),
        hr: () => <hr className="border-border my-4" />,

        // ── Links — vault paths become FileLink chips ─────────────────────
        a: ({ href, children }) => {
          if (href && isVaultPath(href)) {
            return <FileLink path={href}>{children}</FileLink>
          }
          return (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary underline underline-offset-2 hover:opacity-80"
            >
              {children}
            </a>
          )
        },

        table: ({ children }) => (
          <div className="overflow-x-auto mb-3">
            <table className="w-full border-collapse text-sm">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className="border border-border px-3 py-1.5 bg-muted font-semibold text-left">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="border border-border px-3 py-1.5">{children}</td>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}