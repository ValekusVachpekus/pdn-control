FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

# Бэкенд доступен через nginx-прокси на том же origin, поэтому VITE_API_BASE пустой,
# а MOCK выключаем — фронт ходит в реальный /api/.
ENV VITE_USE_MOCK=false
ENV VITE_API_BASE=
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
