import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// Se muestra cuando el servidor de Next.js no pudo consultar la API
export function AvisoSinApi({ mensaje }: { mensaje: string }) {
  return (
    <Alert variant="destructive">
      <AlertTitle>No pudimos consultar el modelo</AlertTitle>
      <AlertDescription>
        {mensaje} La página funciona, pero el servicio que hace las
        predicciones no respondió. Vuelva a intentar en unos minutos.
      </AlertDescription>
    </Alert>
  );
}
