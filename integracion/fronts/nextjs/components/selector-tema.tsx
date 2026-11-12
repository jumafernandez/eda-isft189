"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import { Button } from "@/components/ui/button";

export function SelectorTema() {
  const { resolvedTheme, setTheme } = useTheme();

  function alternar() {
    setTheme(resolvedTheme === "dark" ? "light" : "dark");
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={alternar}
      aria-label="Cambiar entre tema claro y oscuro"
      className="text-[#e6d3b3] hover:bg-white/10 hover:text-white"
    >
      {/* Se dibujan los dos íconos y el CSS muestra el que corresponde */}
      <Sun className="hidden dark:block" />
      <Moon className="dark:hidden" />
    </Button>
  );
}
