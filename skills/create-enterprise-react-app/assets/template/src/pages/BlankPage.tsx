import { Check, Code2 } from 'lucide-react'

export function BlankPage() {
  return (
    <div className="blank-page">
      <div className="page-index" aria-hidden="true">
        00
      </div>

      <div className="blank-visual" aria-hidden="true">
        <span className="visual-line visual-line-one" />
        <span className="visual-line visual-line-two" />
        <span className="visual-node visual-node-one" />
        <span className="visual-node visual-node-two" />
      </div>

      <div className="blank-copy">
        <p className="eyebrow">Workspace canvas</p>
        <h1>A clear place for the first module.</h1>
        <p className="blank-description">
          The application shell is ready. Add the next feature when the product shape is
          known.
        </p>

        <div className="readiness-list" aria-label="Project readiness">
          <span>
            <Check size={14} strokeWidth={2} aria-hidden="true" /> Shell ready
          </span>
          <span>
            <Code2 size={14} strokeWidth={2} aria-hidden="true" /> API boundary reserved
          </span>
        </div>
      </div>
    </div>
  )
}
