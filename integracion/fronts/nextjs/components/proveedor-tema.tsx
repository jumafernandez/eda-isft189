"use client";

// next-themes recuerda el tema elegido (claro u oscuro) y lo aplica
// agregando la clase "dark" a la etiqueta <html>
import { ThemeProvider } from "next-themes";

export function ProveedorTema({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </ThemeProvider>
  );
}
