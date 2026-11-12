# Imagen del front Next.js, en tres etapas: solo la última llega a producción

# 1. Dependencias
FROM node:24-alpine AS dependencias
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 2. Compilación
FROM node:24-alpine AS compilacion
WORKDIR /app
COPY --from=dependencias /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 3. Ejecución: solo lo que el servidor necesita para funcionar
FROM node:24-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY --from=compilacion /app/.next/standalone ./
COPY --from=compilacion /app/.next/static ./.next/static

# Usuario sin privilegios (la imagen de Node ya trae uno llamado "node")
USER node

EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
