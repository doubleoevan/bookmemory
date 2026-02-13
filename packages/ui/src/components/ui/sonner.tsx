"use client";

import { toast, Toaster as SonnerToaster, type ToasterProps } from "sonner";

export { toast };

export function Toaster(props: ToasterProps) {
  return <SonnerToaster richColors closeButton position="top-right" {...props} />;
}
