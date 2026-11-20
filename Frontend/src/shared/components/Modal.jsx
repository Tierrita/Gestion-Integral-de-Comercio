import { useEffect, useId, useRef } from 'react'
import styles from './Modal.module.css'

export default function Modal({
  open, onClose, title, description, children,
  busy = false, closeOnBackdrop = true, closeOnEscape = true,
  size = 'medium', role = 'dialog', className = '',
}) {
  const titleId = useId()
  const descriptionId = useId()
  const panelRef = useRef(null)
  const previousFocusRef = useRef(null)

  useEffect(() => {
    if (!open) return undefined
    previousFocusRef.current = document.activeElement
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const panel = panelRef.current
    const focusables = () => Array.from(panel?.querySelectorAll(
      'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])',
    ) || []).filter((item) => item.getClientRects().length > 0)
    const first = focusables()[0]
    if (first) first.focus()
    else panel?.focus()

    function onKeyDown(event) {
      if (event.key === 'Escape' && closeOnEscape && !busy) {
        event.preventDefault()
        event.stopPropagation()
        onClose?.()
      }
      if (event.key !== 'Tab') return
      const elements = focusables()
      if (!elements.length) {
        event.preventDefault()
        panel?.focus()
        return
      }
      const firstElement = elements[0]
      const lastElement = elements[elements.length - 1]
      if (event.shiftKey && (document.activeElement === firstElement || !panel?.contains(document.activeElement))) {
        event.preventDefault()
        lastElement.focus()
      } else if (!event.shiftKey && (document.activeElement === lastElement || !panel?.contains(document.activeElement))) {
        event.preventDefault()
        firstElement.focus()
      }
    }

    document.addEventListener('keydown', onKeyDown, true)
    return () => {
      document.removeEventListener('keydown', onKeyDown, true)
      document.body.style.overflow = previousOverflow
      const previousFocus = previousFocusRef.current
      if (previousFocus?.isConnected) previousFocus.focus()
    }
  }, [open, busy, closeOnEscape, onClose])

  if (!open) return null

  return (
    <div className={styles.fondo} onMouseDown={(event) => {
      if (event.target === event.currentTarget && closeOnBackdrop && !busy) onClose?.()
    }}>
      <section ref={panelRef} tabIndex={-1} role={role} aria-modal="true"
        aria-labelledby={titleId} aria-describedby={description ? descriptionId : undefined}
        className={`${styles.modal} ${styles[size] || styles.medium} ${className}`.trim()}>
        <header className={styles.encabezado}>
          <div>
            <h2 id={titleId}>{title}</h2>
            {description && <p id={descriptionId}>{description}</p>}
          </div>
          {onClose && <button type="button" className={styles.cerrar} onClick={onClose} disabled={busy} aria-label="Cerrar ventana">×</button>}
        </header>
        <div className={styles.contenido}>{children}</div>
      </section>
    </div>
  )
}
