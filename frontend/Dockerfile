# syntax=docker/dockerfile:1

FROM node:20-bookworm-slim AS base

FROM base AS deps

WORKDIR /app

RUN --mount=type=cache,target=/root/.npm \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci

FROM base AS development

ENV NODE_ENV=development

WORKDIR /app

COPY --link --from=deps /app/node_modules ./node_modules

COPY --link . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS builder

ENV NODE_ENV=production

ARG VITE_API_URL

ARG VITE_WS_URL

ENV VITE_API_URL=$VITE_API_URL \
    VITE_WS_URL=$VITE_WS_URL

WORKDIR /app

COPY --link --from=deps /app/node_modules ./node_modules

COPY --link . .

RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine AS production

USER root

COPY --link nginx/security_headers.conf /etc/nginx/security_headers.conf

COPY --link nginx/default.conf /etc/nginx/conf.d/default.conf

RUN rm /docker-entrypoint.d/20-envsubst-on-templates.sh

USER nginx

COPY --link --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]