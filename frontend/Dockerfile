# node:20-slim (Debian/glibc). Финальный образ — лёгкий nginx:alpine с готовым dist.
FROM node:20-slim AS builder
WORKDIR /app

# npm 10.8.2 (идёт с node:20) имеет баг "Exit handler never called", который
# роняет установку на финализации. Обновляем до npm 11. Плюс поднимаем сетевые
# ретраи/таймауты — реестр npm из РФ бывает медленный, дефолтных ретраев не хватает.
RUN npm install -g npm@11 --no-audit --no-fund
RUN npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 180000 && \
    npm config set fetch-timeout 600000

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
