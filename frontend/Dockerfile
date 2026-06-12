# node:20-slim (Debian/glibc), НЕ alpine: на musl установка нативных зависимостей
# vite (esbuild, rollup) роняет npm с "Exit handler never called". Debian ставит
# их чисто. Финальный образ — лёгкий nginx:alpine, в него едет только готовый dist.
FROM node:20-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --include=dev && \
    test -f node_modules/vite/bin/vite.js || (echo "VITE NOT INSTALLED" && ls node_modules | head -40 && exit 1)

COPY . .

# Бэкенд доступен через nginx-прокси на том же origin, поэтому VITE_API_BASE пустой,
# а MOCK выключаем — фронт ходит в реальный /api/.
ENV VITE_USE_MOCK=false
ENV VITE_API_BASE=

RUN node node_modules/vite/bin/vite.js build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
