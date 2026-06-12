FROM node:20-alpine AS builder
WORKDIR /app

# Форсируем установку devDependencies (vite) максимально жёстко — через env-конфиг
# npm, который перебивает любой .npmrc / NODE_ENV=production в окружении сборки.
# На сервере что-то включало omit=dev, из-за чего vite не ставился.
ENV NODE_ENV=development
ENV NPM_CONFIG_PRODUCTION=false
ENV NPM_CONFIG_OMIT=
ENV NPM_CONFIG_INCLUDE=dev

COPY package*.json ./
# npm install (не ci) надёжнее ставит devDependencies при форсе production=false.
# Сразу проверяем, что vite реально установлен — иначе падаем тут с ясной ошибкой.
RUN npm install --no-audit --no-fund && \
    test -f node_modules/vite/bin/vite.js || (echo "VITE NOT INSTALLED" && ls node_modules | head -40 && exit 1)

COPY . .

# Бэкенд доступен через nginx-прокси на том же origin, поэтому VITE_API_BASE пустой,
# а MOCK выключаем — фронт ходит в реальный /api/.
ENV VITE_USE_MOCK=false
ENV VITE_API_BASE=

# vite через node по пути пакета — не зависим от .bin-симлинка.
RUN node node_modules/vite/bin/vite.js build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
