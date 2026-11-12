"use client";

// Pantalla del escenario "¿qué pasa si...?". Corre en el navegador: por eso
// no llama a la API del modelo, sino a /api/exploracion, la ruta de este
// mismo sitio.
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Curva } from "@/components/curva";
import { Resultado } from "@/components/resultado";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { esquemaVino } from "@/lib/esquema";
import type {
  ErrorDeApi,
  Exploracion,
  InfoModelo,
  Variable,
  Vino,
} from "@/lib/tipos";

type NombreDeVariable = keyof Vino;

/** Separa las variables en los grupos del formulario, sin perder el orden. */
function agrupar(variables: Variable[]) {
  const grupos = new Map<string, Variable[]>();
  for (const variable of variables) {
    const lista = grupos.get(variable.grupo) ?? [];
    lista.push(variable);
    grupos.set(variable.grupo, lista);
  }
  return [...grupos.entries()];
}

export function Explorador({ info }: { info: InfoModelo }) {
  // Punto de partida: la mediana de cada variable
  const valoresIniciales = Object.fromEntries(
    info.variables.map((variable) => [variable.nombre, variable.mediana]),
  ) as Vino;

  const formulario = useForm<Vino>({
    resolver: zodResolver(esquemaVino),
    defaultValues: valoresIniciales,
  });
  const errores = formulario.formState.errors;

  // La medición que se va a mover, el vino que se evaluó y lo que respondió
  // el servidor
  const [variable, setVariable] = useState<NombreDeVariable>("alcohol");
  const [vinoEvaluado, setVinoEvaluado] = useState<Vino | null>(null);
  const [exploracion, setExploracion] = useState<Exploracion | null>(null);
  const [falla, setFalla] = useState<string | null>(null);

  async function explorar(vino: Vino, medicion: NombreDeVariable) {
    setFalla(null);
    let respuesta: Response;
    try {
      respuesta = await fetch("/api/exploracion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ vino, variable: medicion }),
      });
    } catch {
      setExploracion(null);
      setFalla("No se pudo conectar con el sitio. Revise su conexión.");
      return;
    }

    if (respuesta.ok) {
      setVinoEvaluado(vino);
      setExploracion((await respuesta.json()) as Exploracion);
      return;
    }

    // El servidor rechazó el pedido: se muestra el motivo y se marca cada campo
    const error = (await respuesta.json()) as ErrorDeApi;
    setExploracion(null);
    setFalla(error.mensaje);
    for (const problema of error.detalle) {
      formulario.setError(problema.campo as NombreDeVariable, {
        message: problema.mensaje,
      });
    }
  }

  // Al elegir otra medición se vuelve a consultar, si ya hay un vino evaluado
  function cambiarVariable(medicion: NombreDeVariable) {
    setVariable(medicion);
    if (vinoEvaluado) {
      explorar(vinoEvaluado, medicion);
    }
  }

  const metadatos = info.variables.find((v) => v.nombre === variable);

  return (
    <div className="grid items-start gap-10 lg:grid-cols-[1.45fr_1fr]">
      {/* handleSubmit solo llama a explorar si los valores pasan la validación */}
      <form
        onSubmit={formulario.handleSubmit((vino) => explorar(vino, variable))}
        noValidate
      >
        <div className="mb-5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <span>Partir de:</span>
          {info.ejemplos.map((ejemplo) => (
            <Button
              key={ejemplo.nombre}
              type="button"
              variant="outline"
              size="sm"
              className="rounded-full bg-card"
              onClick={() => formulario.reset(ejemplo.valores)}
            >
              {ejemplo.nombre}
            </Button>
          ))}
        </div>

        {agrupar(info.variables).map(([grupo, variables]) => (
          <Card key={grupo} className="mb-4">
            <CardContent>
              <p className="mb-3 text-[0.7rem] font-semibold tracking-[0.12em] text-dorado uppercase">
                {grupo}
              </p>
              {/* Cada campo ocupa tres filas de la grilla (etiqueta, casilla y
                  error) y las comparte con sus vecinos: así las casillas quedan
                  alineadas aunque una etiqueta ocupe dos renglones */}
              <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 sm:grid-cols-4">
                {variables.map((campo) => {
                  const nombre = campo.nombre as NombreDeVariable;
                  const error = errores[nombre];
                  return (
                    <div key={nombre} className="row-span-3 grid grid-rows-subgrid gap-y-1.5">
                      <Label
                        htmlFor={nombre}
                        className="flex-wrap gap-x-1.5 gap-y-0.5 self-end leading-snug"
                      >
                        {campo.etiqueta}
                        {campo.unidad && (
                          <span className="text-xs font-normal text-muted-foreground">
                            {campo.unidad}
                          </span>
                        )}
                      </Label>
                      <Input
                        id={nombre}
                        type="number"
                        step="any"
                        aria-invalid={error ? true : undefined}
                        className="bg-background"
                        {...formulario.register(nombre, { valueAsNumber: true })}
                      />
                      <p className="text-xs text-destructive">{error?.message}</p>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ))}

        <Button
          type="submit"
          size="lg"
          className="h-11 w-full text-base"
          disabled={formulario.formState.isSubmitting}
        >
          {formulario.formState.isSubmitting ? "Consultando..." : "Evaluar y explorar"}
        </Button>
      </form>

      <aside className="space-y-4 lg:sticky lg:top-6" aria-live="polite">
        {falla && (
          <Alert variant="destructive">
            <AlertTitle>No se pudo consultar el modelo</AlertTitle>
            <AlertDescription>{falla}</AlertDescription>
          </Alert>
        )}

        {exploracion && <Resultado prediccion={exploracion.prediccion} />}

        <Card>
          <CardContent>
            <Label htmlFor="variable" className="mb-1.5">
              ¿Qué pasa si cambia...
            </Label>
            <select
              id="variable"
              value={variable}
              onChange={(evento) =>
                cambiarVariable(evento.target.value as NombreDeVariable)
              }
              className="h-9 w-full rounded-lg border border-input bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              {info.variables.map((opcion) => (
                <option key={opcion.nombre} value={opcion.nombre}>
                  {opcion.etiqueta}
                </option>
              ))}
            </select>

            {exploracion && vinoEvaluado && metadatos ? (
              <div className="mt-4">
                <Curva
                  puntos={exploracion.puntos}
                  variable={metadatos}
                  valorActual={vinoEvaluado[exploracion.variable]}
                />
                <p className="mt-3 text-xs text-muted-foreground">
                  La curva muestra cómo responde el modelo, no una relación de
                  causa y efecto: en un vino real, cambiar una medición modifica
                  también las demás.
                </p>
              </div>
            ) : (
              <p className="mt-3 text-sm text-muted-foreground">
                Presione <strong className="text-foreground">Evaluar y explorar</strong>{" "}
                para ver cómo cambia la calidad estimada cuando esta medición
                recorre su rango y las demás quedan fijas.
              </p>
            )}
          </CardContent>
        </Card>
      </aside>
    </div>
  );
}
