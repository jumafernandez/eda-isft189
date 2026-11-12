import { Suspense } from "react";

import { AvisoSinApi } from "@/components/aviso-sin-api";
import { EncabezadoPagina } from "@/components/encabezado-pagina";
import { Explorador } from "@/components/explorador";
import { Skeleton } from "@/components/ui/skeleton";
import { FallaDeApi, obtenerInfoDelModelo } from "@/lib/api";

export default function PaginaInicio() {
  return (
    <>
      <EncabezadoPagina
        volanta="Exploración"
        titulo="¿Qué pasa si cambia una medición?"
        bajada="Parta de un vino, elija una medición y vea cómo cambia la calidad estimada cuando esa medición sube o baja y las demás quedan fijas."
      />
      {/* Lo de afuera se envía enseguida. Lo de adentro de Suspense depende
          de la API: mientras llega, se ve el contenido de "fallback". */}
      <Suspense fallback={<Skeleton className="h-96 w-full rounded-xl" />}>
        <Catador />
      </Suspense>
    </>
  );
}

// Componente de servidor: pide los metadatos a la API con la clave privada
// y le entrega a la pantalla solo los datos que necesita mostrar
async function Catador() {
  try {
    const info = await obtenerInfoDelModelo();
    return <Explorador info={info} />;
  } catch (falla) {
    if (falla instanceof FallaDeApi) {
      return <AvisoSinApi mensaje={falla.message} />;
    }
    throw falla;
  }
}
