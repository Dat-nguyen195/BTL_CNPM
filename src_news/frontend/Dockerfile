FROM node:22-alpine AS build
WORKDIR /frontend
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html *.ts *.js ./
COPY src ./src
ENV VITE_API_BASE_URL=/
RUN npm run build

FROM nginx:1.28-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /frontend/dist /usr/share/nginx/html
