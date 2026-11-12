import { Suspense } from "react";

import { AvisoSinApi } from "@/components/aviso-sin-api";
import { EncabezadoPagina } from "@/components/encabezado-pagina";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FallaDeApi, obtenerInfoDelModelo } from "@/lib/api";
import { cn } from "@/lib/utils";

export const metadata = { title: "El modelo - Bodega Los Aromos" };

export default function PaginaModelo() {
  return (
    <>
      <EncabezadoPagina
        volanta="Ficha técnica"
        titulo="El modelo"
        bajada="Lo que la API informa sobre el modelo que está sirviendo."
      />
      <Suspense fallback={<Skeleton className="h-96 w-full rounded-xl" />}>
        <Ficha />
      </Suspense>
    </>
  );
}

function enCastellano(numero: number, decimales = 3) {
  return numero.toLocaleString("es-AR", { maximumFractionDigits: decimales });
}

function Dato(props: { rotulo: string; valor: string; nota: string }) {
  return (
    <Card>
      <CardContent>
        <p className="text-xs text-muted-foreground">{props.rotulo}</p>
        <p className="font-heading text-3xl leading-snug font-semibold text-primary">
          {props.valor}
        </p>
        <p className="text-xs text-muted-foreground">{props.nota}</p>
      </CardContent>
    </Card>
  );
}

async function Ficha() {
  let info;
  try {
    info = await obtenerInfoDelModelo();
  } catch (falla) {
    if (falla instanceof FallaDeApi) {
      return <AvisoSinApi mensaje={falla.message} />;
    }
    throw falla;
  }

  return (
    <div className="space-y-10">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Dato rotulo="Modelo" valor={info.version} nota={info.nombre} />
        <Dato
          rotulo="Entrenado el"
          valor={info.fecha_entrenamiento.split("-").reverse().join("/")}
          nota={`Con ${enCastellano(info.filas_entrenamiento)} vinos`}
        />
        <Dato
          rotulo="Accuracy"
          valor={`${enCastellano(info.accuracy_prueba * 100, 1)} %`}
          nota={`Sobre ${enCastellano(info.filas_prueba)} vinos de prueba`}
        />
        <Dato
          rotulo="F1 macro"
          valor={enCastellano(info.f1_macro_prueba)}
          nota="Promedio parejo entre las tres clases"
        />
      </div>

      <section>
        <h2 className="mb-2 font-heading text-2xl font-semibold">Matriz de confusión</h2>
        <p className="mb-4 max-w-[62ch] text-muted-foreground">
          Cada fila es la calidad real y cada columna, la que predijo el modelo.
          La diagonal reúne los aciertos.
        </p>
        <Card className="max-w-md py-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Real \ Predicha</TableHead>
                {info.clases.map((clase) => (
                  <TableHead key={clase} className="text-center capitalize">
                    {clase}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {info.matriz_confusion.map((fila, real) => (
                <TableRow key={info.clases[real]}>
                  <TableHead className="capitalize">{info.clases[real]}</TableHead>
                  {fila.map((cantidad, predicha) => (
                    <TableCell
                      key={info.clases[predicha]}
                      className={cn(
                        "text-center",
                        real === predicha && "bg-alta/15 font-semibold text-alta",
                      )}
                    >
                      {cantidad}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </section>

      <section>
        <h2 className="mb-4 font-heading text-2xl font-semibold">Variables de entrada</h2>
        <Card className="py-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Variable</TableHead>
                <TableHead>Grupo</TableHead>
                <TableHead>Unidad</TableHead>
                <TableHead className="text-right">Mínimo</TableHead>
                <TableHead className="text-right">Mediana</TableHead>
                <TableHead className="text-right">Máximo</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {info.variables.map((variable) => (
                <TableRow key={variable.nombre}>
                  <TableCell className="font-medium">{variable.etiqueta}</TableCell>
                  <TableCell>{variable.grupo}</TableCell>
                  <TableCell>{variable.unidad || "-"}</TableCell>
                  <TableCell className="text-right">
                    {enCastellano(variable.minimo, 5)}
                  </TableCell>
                  <TableCell className="text-right">
                    {enCastellano(variable.mediana, 5)}
                  </TableCell>
                  <TableCell className="text-right">
                    {enCastellano(variable.maximo, 5)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </section>
    </div>
  );
}
