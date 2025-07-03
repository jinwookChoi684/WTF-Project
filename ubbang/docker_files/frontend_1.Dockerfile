# frontend_1/Dockerfile

# 1. Build Stage
FROM node:20-alpine AS builder
WORKDIR /app

# pnpm-lock.yaml이 있으므로 pnpm을 사용합니다.
RUN npm install -g pnpm

# 소스 경로를 명확히 해줍니다.
COPY frontend_1/package.json frontend_1/pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

COPY frontend_1/ . 
RUN pnpm build

# 2. Production Stage
FROM node:20-alpine
WORKDIR /app

RUN npm install -g pnpm

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

EXPOSE 3000
CMD ["pnpm", "start"]
