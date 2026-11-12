# Front con Next.js

Escenario de exploración del ejemplo de integración: se parte de un vino, se elige una medición y se ve cómo cambia la calidad estimada cuando esa medición recorre su rango. Es una aplicación con Next.js (App Router), TypeScript, Tailwind y shadcn/ui. El navegador nunca llama a la API del modelo; lo hace el servidor de Next.js, que es el único que conoce la clave privada.

```bash
cp .env.example .env.local     # en Windows: copy .env.example .env.local
npm install
npm run dev                    # http://localhost:3000
```

Necesita la API levantada (ver el [README de integracion](../../README.md)).

| Archivo | Qué hace |
|:--|:--|
| `lib/api.ts` | Cliente de la API del modelo. Solo corre en el servidor y agrega la clave. |
| `app/api/exploracion/route.ts` | Route Handler: recibe el vino y la medición, arma las variantes y pide el lote a la API. |
| `app/page.tsx` | Pide los metadatos en el servidor y arma la página. |
| `components/explorador.tsx` | Formulario con react-hook-form y validación con zod, resultado y selector de la medición. |
| `components/curva.tsx` | Curva de probabilidades, dibujada en SVG sin librerías de gráficos. |
| `lib/esquema.ts` | Reglas de validación, compartidas entre el navegador y el servidor. |
| `lib/api-tipos.ts` | Tipos generados desde la descripción OpenAPI de la API. No se edita a mano. |
| `app/modelo/page.tsx` | Ficha del modelo. |

Si cambia el contrato de la API, vuelva a generar los tipos con la API levantada:

```bash
npm run tipos
```

Para desplegarlo en Vercel, vea [docs/despliegue.md](../../docs/despliegue.md).
