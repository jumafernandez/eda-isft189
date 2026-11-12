// Volanta, título y bajada: el mismo encabezado en todas las pantallas
export function EncabezadoPagina(props: {
  volanta: string;
  titulo: string;
  bajada: string;
}) {
  return (
    <div className="mb-8">
      <p className="mb-1.5 text-xs font-semibold tracking-[0.16em] text-dorado uppercase">
        {props.volanta}
      </p>
      <h1 className="font-heading text-4xl leading-tight font-semibold text-primary">
        {props.titulo}
      </h1>
      <p className="mt-2 max-w-[62ch] text-muted-foreground">{props.bajada}</p>
    </div>
  );
}
