# ---- Stage 1: Build ----
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build -- --configuration=production

# ---- Stage 2: Serve with Nginx ----
FROM nginx:alpine AS production

# Copiar la build de Angular
COPY --from=build /app/dist/bancolombia-rag-frontend/browser /usr/share/nginx/html

# Configuración Nginx para SPA (redirect all to index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
