// Validación del formulario con zod. Se usa dos veces: en el navegador,
// para avisar del error apenas se escribe, y en el servidor, antes de
// llamar a la API. Los rangos son los mismos que define la API.
import { z } from "zod";

import type { Vino } from "./tipos";

function medicion(minimo: number, maximo: number) {
  return z
    .number({ error: "Debe ser un número." })
    .min(minimo, `Debe ser mayor o igual a ${minimo}.`)
    .max(maximo, `Debe ser menor o igual a ${maximo}.`);
}

// "satisfies" comprueba que el esquema tenga exactamente los campos de Vino,
// el tipo generado desde la API
export const esquemaVino = z.object({
  acidez_fija: medicion(0, 20),
  acidez_volatil: medicion(0, 2),
  acido_citrico: medicion(0, 2),
  ph: medicion(2, 5),
  dioxido_azufre_libre: medicion(0, 300),
  dioxido_azufre_total: medicion(0, 500),
  sulfatos: medicion(0, 3),
  cloruros: medicion(0, 1),
  azucar_residual: medicion(0, 70),
  densidad: medicion(0.98, 1.05),
  alcohol: medicion(0, 20),
}) satisfies z.ZodType<Vino>;
