import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Genera una versión mínima del servidor, pensada para la imagen de Docker
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
