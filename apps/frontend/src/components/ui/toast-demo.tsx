import * as Toast from "@radix-ui/react-toast";
import { useEffect, useRef, useState } from "react";
import { clsx } from "clsx";

export function ToastDemo(): JSX.Element {
  const [open, setOpen] = useState(false);
  const timerRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    return () => window.clearTimeout(timerRef.current);
  }, []);

  return (
    <Toast.Provider swipeDirection="right">
      <button
        type="button"
        className="rounded-full border border-emerald-400/60 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-200 transition hover:border-emerald-300 hover:bg-emerald-500/20"
        onClick={() => {
          setOpen(false);
          window.clearTimeout(timerRef.current);
          timerRef.current = window.setTimeout(() => {
            setOpen(true);
          }, 100);
        }}
      >
        Show pipeline status
      </button>

      <Toast.Root
        className={clsx(
          "pointer-events-auto flex w-80 flex-col gap-1 rounded-xl border border-slate-800 bg-slate-900/90 px-5 py-4 text-left shadow-lg shadow-emerald-500/20",
          "data-[state=open]:animate-in data-[state=open]:fade-in data-[state=open]:slide-in-from-top-1/2",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out"
        )}
        open={open}
        onOpenChange={setOpen}
      >
        <Toast.Title className="text-base font-semibold text-slate-100">Pipelines healthy</Toast.Title>
        <Toast.Description className="text-sm text-slate-400">
          All ingestion and retrieval orchestrations reported success in the last 15 minutes.
        </Toast.Description>
        <Toast.Close className="self-end text-xs font-medium uppercase tracking-wide text-emerald-300">
          Dismiss
        </Toast.Close>
      </Toast.Root>
      <Toast.Viewport className="fixed top-5 right-5 z-50 outline-none" />
    </Toast.Provider>
  );
}
