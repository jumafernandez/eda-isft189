// Tipos de los datos que viajan entre este front y la API.
// No se escriben a mano: salen de lib/api-tipos.ts, que se genera a partir
// de la descripción OpenAPI de la API con el comando "npm run tipos".
// Si el contrato de la API cambia, TypeScript marca qué hay que ajustar acá.
import type { components } from "./api-tipos";

type Esquemas = components["schemas"];

export type Vino = Esquemas["Vino"];
export type Variable = Esquemas["Variable"];
export type InfoModelo = Esquemas["InfoModelo"];
export type RespuestaPrediccion = Esquemas["RespuestaPrediccion"];
export type ErrorDeApi = Esquemas["Error"];
export type Calidad = RespuestaPrediccion["calidad"];
export type Probabilidades = Esquemas["Probabilidades"];
export type RespuestaLote = Esquemas["RespuestaLote"];

// Los dos tipos que siguen son propios de este front: describen lo que
// devuelve su ruta /api/exploracion

/** Un punto de la curva: un valor de la medición y lo que predice el modelo. */
export type PuntoDeCurva = { valor: number; probabilidades: Probabilidades };

export type Exploracion = {
  prediccion: RespuestaPrediccion; // la del vino tal como se cargó
  variable: keyof Vino; // la medición que se movió
  puntos: PuntoDeCurva[]; // la curva, del valor mínimo al máximo
};
