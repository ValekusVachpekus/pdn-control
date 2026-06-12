FROM node:20-alpine AS builder
WORKDIR /app

# Гарантируем установку devDependencies (vite). Если в окружении сборки выставлен
# NODE_ENV=production, npm неявно применяет omit=dev и пропускает vite — поэтому
# явно форсируем development на этапе сборки (образ-билдер всё равно отбрасывается).
ENV NODE_ENV=development

COPY package*.json ./
RUN npm ci --include=dev

COPY . .

# Бэкенд доступен через nginx-прокси на том же origin, поэтому VITE_API_BASE пустой,
# а MOCK выключаем — фронт ходит в реальный /api/.
ENV VITE_USE_MOCK=false
ENV VITE_API_BASE=

# Вызываем бинарь vite напрямую — не зависим от PATH и npm-скриптов; если vite
# не установился, упадёт здесь с понятной ошибкой раньше.
RUN ./node_modules/.bin/vite build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
