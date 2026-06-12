FROM node:20-alpine AS builder
WORKDIR /app

# Гарантируем установку devDependencies (vite). NODE_ENV=production у npm
# подразумевает omit=dev — форсируем development на этапе сборки.
ENV NODE_ENV=development

COPY package*.json ./
RUN npm ci --include=dev

COPY . .

# Бэкенд доступен через nginx-прокси на том же origin, поэтому VITE_API_BASE пустой,
# а MOCK выключаем — фронт ходит в реальный /api/.
ENV VITE_USE_MOCK=false
ENV VITE_API_BASE=

# Диагностика: показать, что реально установилось (видно в логах сборки).
RUN echo "=== .bin/vite ===" && (ls -la node_modules/.bin/vite || echo "NO .bin/vite symlink") && \
    echo "=== vite package ===" && (ls -la node_modules/vite/bin/vite.js || echo "NO vite package")

# Запускаем vite через node напрямую по пути пакета — не зависим от .bin-симлинка
# (который на некоторых Docker-ФС не создаётся). Если пакет vite установлен —
# это сработает; если нет — упадёт с понятной ошибкой.
RUN node node_modules/vite/bin/vite.js build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
