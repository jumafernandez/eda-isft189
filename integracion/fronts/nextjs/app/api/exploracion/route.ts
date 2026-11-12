// Route Handler del escenario "¿qué pasa si...?".
// El navegador envía un vino y el nombre de una medición. Este código, que
// corre en el servidor, arma copias del vino en las que solo cambia esa
// medición y le pide todas las predicciones juntas a la API del modelo,
// con la clave privada. La clave nunca viaja al navegador.
import { z } from "zod";

import { FallaDeApi, obtenerInfoDelModelo, predecirLote } from "@/lib/api";
import { esquemaVino } from "@/lib/esquema";
import type { Exploracion, Vino } from "@/lib/tipos";

const PUNTOS = 40; // cantidad de tramos de la curva

const esquemaPedido = z.object({
  vino: esquemaVino,
  variable: esquemaVino.keyof(),
});

export async function POST(request: Request) {
  const cuerpo = await request.json().catch(() => null);

  // Se valida de nuevo en el servidor: el pedido pudo no venir del formulario
  const revision = esquemaPedido.safeParse(cuerpo);
  if (!revision.success) {
    const detalle = revision.error.issues.map((problema) => ({
      // "vino.alcohol" pasa a "alcohol", el nombre del campo del formulario
      campo: problema.path.filter((parte) => parte !== "vino").join("."),
      mensaje: problema.message,
    }));
    return Response.json(
      { error: "datos_invalidos", mensaje: "Revise los valores.", detalle },
      { status: 422 },
    );
  }
  const { vino, variable } = revision.data;

  try {
    // El rango a recorrer sale de los metadatos del modelo
    const info = await obtenerInfoDelModelo();
    const rango = info.variables.find((v) => v.nombre === variable);
    if (!rango) {
      throw new FallaDeApi(500, {
        error: "contrato_distinto",
        mensaje: "La API no informa esa medición. Ejecute npm run tipos.",
        detalle: [],
      });
    }

    // Valores parejos entre el mínimo y el máximo observados en los datos
    const valores: number[] = [];
    for (let paso = 0; paso <= PUNTOS; paso++) {
      const avance = paso / PUNTOS;
      valores.push(rango.minimo + (rango.maximo - rango.minimo) * avance);
    }
    const variantes: Vino[] = valores.map((valor) => ({
      ...vino,
      [variable]: valor,
    }));

    // Un solo pedido por lote: primero el vino original, después sus variantes
    const lote = await predecirLote([vino, ...variantes]);
    const [original, ...resto] = lote.predicciones;

    const respuesta: Exploracion = {
      prediccion: { ...original, version_modelo: lote.version_modelo },
      variable,
      puntos: resto.map((prediccion, posicion) => ({
        valor: valores[posicion],
        probabilidades: prediccion.probabilidades,
      })),
    };
    return Response.json(respuesta);
  } catch (falla) {
    if (falla instanceof FallaDeApi) {
      return Response.json(falla.cuerpo, { status: falla.estado });
    }
    throw falla;
  }
}
