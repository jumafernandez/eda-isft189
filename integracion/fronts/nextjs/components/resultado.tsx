import { Card, CardContent } from "@/components/ui/card";
import type { Calidad, RespuestaPrediccion } from "@/lib/tipos";
import { cn } from "@/lib/utils";

const CLASES: Calidad[] = ["baja", "media", "alta"];

// Tailwind necesita ver los nombres de clase completos en el código,
// por eso no se arman pegando textos
const COLOR_TEXTO: Record<Calidad, string> = {
  baja: "text-baja",
  media: "text-media",
  alta: "text-alta",
};
const COLOR_BARRA: Record<Calidad, string> = {
  baja: "bg-baja",
  media: "bg-media",
  alta: "bg-alta",
};

export function Resultado({ prediccion }: { prediccion: RespuestaPrediccion }) {
  return (
    <Card className="shadow-lg shadow-primary/5">
      <CardContent>
        <p className="text-xs text-muted-foreground">Calidad estimada</p>
        <p
          className={cn(
            "mb-3 font-heading text-5xl leading-tight font-semibold capitalize",
            COLOR_TEXTO[prediccion.calidad],
          )}
        >
          {prediccion.calidad}
        </p>

        {CLASES.map((clase) => {
          const porcentaje = Math.round(prediccion.probabilidades[clase] * 100);
          return (
            <div
              key={clase}
              className="mt-1.5 grid grid-cols-[3.2rem_1fr_2.8rem] items-center gap-2.5 text-sm"
            >
              <span>{clase}</span>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div
                  className={cn("h-full rounded-full transition-all", COLOR_BARRA[clase])}
                  style={{ width: `${porcentaje}%` }}
                />
              </div>
              <span className="text-right">{porcentaje} %</span>
            </div>
          );
        })}

        <p className="mt-4 text-xs text-muted-foreground">
          Estimación de un modelo estadístico, versión {prediccion.version_modelo}.
          No reemplaza una cata.
        </p>
      </CardContent>
    </Card>
  );
}
