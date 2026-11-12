"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { SelectorTema } from "@/components/selector-tema";
import { cn } from "@/lib/utils";

const ENLACES = [
  { href: "/", texto: "Explorar" },
  { href: "/modelo", texto: "El modelo" },
];

export function Cabecera() {
  const rutaActual = usePathname();

  return (
    <header className="bg-cabecera">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-x-8 gap-y-2 px-6 py-3.5">
        <Link href="/" className="flex items-baseline gap-3">
          <strong className="font-heading text-xl font-semibold text-[#f3e6d0]">
            Bodega Los Aromos
          </strong>
          <span className="text-[0.7rem] font-semibold tracking-[0.14em] text-[#d1a85a] uppercase">
            Catador virtual
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {ENLACES.map((enlace) => (
            <Link
              key={enlace.href}
              href={enlace.href}
              aria-current={rutaActual === enlace.href ? "page" : undefined}
              className={cn(
                "rounded-full px-3.5 py-1.5 text-sm text-[#e6d3b3] hover:text-white",
                rutaActual === enlace.href && "bg-[#6b1f2e] text-white",
              )}
            >
              {enlace.texto}
            </Link>
          ))}
          <SelectorTema />
        </nav>
      </div>
    </header>
  );
}
