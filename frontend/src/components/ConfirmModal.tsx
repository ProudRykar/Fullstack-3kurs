import { useEffect, useRef } from 'react';

const styles = `
  .confirm-dialog::backdrop {
    background-color: rgba(0, 0, 0, 0.6);
  }
`;

interface ConfirmModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmModal({ open, title, message, confirmText = 'Да', cancelText = 'Нет', onConfirm, onCancel }: ConfirmModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const styleRef = useRef<HTMLStyleElement | null>(null);

  useEffect(() => {
    if (!styleRef.current) {
      const s = document.createElement('style');
      s.textContent = styles;
      document.head.appendChild(s);
      styleRef.current = s;
    }
    return () => {
      if (styleRef.current) {
        styleRef.current.remove();
        styleRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    if (open && !el.open) {
      el.showModal();
    } else if (!open && el.open) {
      el.close();
    }
  }, [open]);

  if (!open) return null;

  return (
    <dialog
      ref={dialogRef}
      className="fixed inset-0 m-auto rounded-xl shadow-2xl p-6 max-w-sm bg-[#1E293B] text-white border border-border confirm-dialog"
      onClose={onCancel}
    >
      <h3 className="text-lg font-semibold mb-2 text-text">{title}</h3>
      <p className="text-text-muted mb-6">{message}</p>
      <div className="flex justify-end gap-3">
        <button
          onClick={onCancel}
          className="px-4 py-2 border border-border rounded-lg bg-bg-secondary text-text hover:bg-border transition-colors cursor-pointer"
        >
          {cancelText}
        </button>
        <button
          onClick={onConfirm}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors cursor-pointer font-medium"
        >
          {confirmText}
        </button>
      </div>
    </dialog>
  );
}
