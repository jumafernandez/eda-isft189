// Curva de probabilidades: cómo cambia la predicción del modelo cuando una
// medición recorre su rango y las demás quedan fijas.
// Es un dibujo SVG hecho a mano, sin ninguna librería de gráficos.
import type { Calidad, PuntoDeCurva, Variable } from "@/lib/tipos";

const CLASES: Calidad[] = ["baja", "media", "alta"];
const TRAZO: Record<Calidad, string> = {
  baja: "stroke-baja",
  media: "stroke-media",
  alta: "stroke-alta",
};
const PUNTO: Record<Calidad, string> = {
  baja: "bg-baja",
  media: "bg-media",
  alta: "bg-alta",
};

// Medidas del dibujo, en unidades propias del SVG
const ANCHO = 340;
const ALTO = 190;
const MARGEN = { izquierda: 38, derecha: 10, arriba: 10, abajo: 26 };

// Escribe un número con cuatro cifras significativas: 12,49 - 0,9871 - 289
function enCastellano(numero: number) {
  return numero.toLocaleString("es-AR", { maximumSignificantDigits: 4 });
}

export function Curva(props: {
  puntos: PuntoDeCurva[];
  variable: Variable;
  valorActual: number;
}) {
  const { puntos, variable, valorActual } = props;
  const anchoUtil = ANCHO - MARGEN.izquierda - MARGEN.derecha;
  const altoUtil = ALTO - MARGEN.arriba - MARGEN.abajo;

  // Convierten un valor de la medición y una probabilidad en coordenadas
  function x(valor: number) {
    const avance = (valor - variable.minimo) / (variable.maximo - variable.minimo);
    return MARGEN.izquierda + avance * anchoUtil;
  }
  function y(probabilidad: number) {
    return MARGEN.arriba + (1 - probabilidad) * altoUtil;
  }

  // El punto donde la probabilidad de calidad alta es mayor y donde es menor
  let mejor = puntos[0];
  let peor = puntos[0];
  for (const punto of puntos) {
    if (punto.probabilidades.alta > mejor.probabilidades.alta) mejor = punto;
    if (punto.probabilidades.alta < peor.probabilidades.alta) peor = punto;
  }

  const actualEnRango =
    valorActual >= variable.minimo && valorActual <= variable.maximo;
  const unidad = variable.unidad ? ` ${variable.unidad}` : "";

  return (
    <div>
      <svg
        viewBox={`0 0 ${ANCHO} ${ALTO}`}
        role="img"
        aria-label={`Probabilidad de cada calidad según ${variable.etiqueta}`}
        className="w-full"
      >
        {/* Líneas de referencia en 0, 50 y 100 % */}
        {[0, 0.5, 1].map((nivel) => (
          <g key={nivel}>
            <line
              x1={MARGEN.izquierda}
              x2={ANCHO - MARGEN.derecha}
              y1={y(nivel)}
              y2={y(nivel)}
              className="stroke-border"
            />
            <text
              x={MARGEN.izquierda - 6}
              y={y(nivel) + 3.5}
              textAnchor="end"
              className="fill-muted-foreground text-[10px]"
            >
              {nivel * 100} %
            </text>
          </g>
        ))}

        {/* El valor que tiene hoy el vino */}
        {actualEnRango && (
          <line
            x1={x(valorActual)}
            x2={x(valorActual)}
            y1={MARGEN.arriba}
            y2={ALTO - MARGEN.abajo}
            strokeDasharray="3 3"
            className="stroke-foreground/50"
          />
        )}

        {/* Una línea por clase */}
        {CLASES.map((clase) => (
          <polyline
            key={clase}
            fill="none"
            strokeWidth={2.2}
            strokeLinejoin="round"
            className={TRAZO[clase]}
            points={puntos
              .map((punto) => `${x(punto.valor)},${y(punto.probabilidades[clase])}`)
              .join(" ")}
          />
        ))}

        {/* Extremos del rango, en el eje horizontal */}
        <text
          x={MARGEN.izquierda}
          y={ALTO - 8}
          className="fill-muted-foreground text-[10px]"
        >
          {enCastellano(variable.minimo)}
        </text>
        <text
          x={ANCHO - MARGEN.derecha}
          y={ALTO - 8}
          textAnchor="end"
          className="fill-muted-foreground text-[10px]"
        >
          {enCastellano(variable.maximo)}
          {unidad}
        </text>
      </svg>

      <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {CLASES.map((clase) => (
          <span key={clase} className="flex items-center gap-1.5">
            <span className={`size-2 rounded-full ${PUNTO[clase]}`} />
            calidad {clase}
          </span>
        ))}
        {actualEnRango && <span>línea punteada: valor actual</span>}
      </div>

      <p className="mt-3 text-sm">
        Moviendo solo esta medición, la probabilidad de calidad alta va de{" "}
        <strong>{Math.round(peor.probabilidades.alta * 100)} %</strong> (con{" "}
        {enCastellano(peor.valor)}
        {unidad}) a{" "}
        <strong>{Math.round(mejor.probabilidades.alta * 100)} %</strong> (con{" "}
        {enCastellano(mejor.valor)}
        {unidad}).
      </p>
    </div>
  );
}
