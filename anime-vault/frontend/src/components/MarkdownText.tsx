import { Fragment } from 'react'

/** Split a line on **bold** markers into text runs and strong runs. */
function renderInline(text: string, keyPrefix: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return (
        <strong key={`${keyPrefix}-b${i}`} className="font-semibold">
          {part.slice(2, -2)}
        </strong>
      )
    }
    return <Fragment key={`${keyPrefix}-t${i}`}>{part}</Fragment>
  })
}

interface MarkdownTextProps {
  content: string
  className?: string
}

/**
 * Minimal renderer for the assistant's replies.
 *
 * The backend formats answers as plain text with `**名字**` emphasis, so the
 * chat bubble only needs bold runs and preserved newlines. A full markdown
 * library would add a parser and an XSS surface for syntax we never emit.
 */
export default function MarkdownText({ content, className }: MarkdownTextProps) {
  const lines = content.split('\n')
  return (
    <div className={className}>
      {lines.map((line, i) => (
        <Fragment key={`line-${i}`}>
          {renderInline(line, `line-${i}`)}
          {i < lines.length - 1 && <br />}
        </Fragment>
      ))}
    </div>
  )
}
