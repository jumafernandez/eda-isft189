// Cliente de la API del modelo.
// La línea "server-only" hace que la compilación falle si alguien importa
// este archivo desde un componente del navegador: así la clave privada
// no puede terminar, por error, en el código que se envía al público.
import "server-only";

import type { ErrorDeApi, InfoModelo, RespuestaLote, Vino } from "./tipos";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const API_KEY = process.env.API_KEY ?? "";

/** La API no respondió o respondió con un error. */
export class FallaDeApi extends Error {
  constructor(
    public estado: number,
    public cuerpo: ErrorDeApi,
  ) {
    super(cuerpo.mensaje);
  }
}

async function llamarApi<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(API_URL + ruta, {
      ...opciones,
      headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
    });
  } catch {
    throw new FallaDeApi(503, {
      error: "sin_conexion",
      mensaje: "No se pudo conectar con la API del modelo.",
      detalle: [],
    });
  }

  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    throw new FallaDeApi(respuesta.status, {
      error: cuerpo?.error ?? "error",
      mensaje: cuerpo?.mensaje ?? `La API respondió con el código ${respuesta.status}.`,
      detalle: cuerpo?.detalle ?? [],
    });
  }
  return cuerpo as T;
}

export function obtenerInfoDelModelo() {
  return llamarApi<InfoModelo>("/v1/model-info");
}

export function predecirLote(vinos: Vino[]) {
  return llamarApi<RespuestaLote>("/v1/predict/batch", {
    method: "POST",
    body: JSON.stringify({ vinos }),
  });
}
