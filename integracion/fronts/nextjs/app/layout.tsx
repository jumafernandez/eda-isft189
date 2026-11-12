import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";

import { Cabecera } from "@/components/cabecera";
import { ProveedorTema } from "@/components/proveedor-tema";

import "./globals.css";

// next/font descarga las tipografías al compilar y las sirve desde
// la propia aplicación: el navegador no le pide nada a Google
const inter = Inter({ variable: "--font-sans", subsets: ["latin"] });
const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Catador virtual - Bodega Los Aromos",
  description: "Estima la calidad de un vino a partir de sus mediciones de laboratorio.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    // suppressHydrationWarning: next-themes cambia la clase de <html>
    // antes de que React tome el control de la página
    <html
      lang="es"
      suppressHydrationWarning
      className={`${inter.variable} ${playfair.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <ProveedorTema>
          <Cabecera />
          <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-10">
            {children}
          </main>
          <footer className="pb-8 text-center text-xs text-muted-foreground">
            Front con Next.js y shadcn/ui - Práctica Profesional, ISFT N°189
          </footer>
        </ProveedorTema>
      </body>
    </html>
  );
}
