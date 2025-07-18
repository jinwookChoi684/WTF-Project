# 1. 빌드 환경 설정
FROM node:18-alpine AS builder

# 일반적인 node-gyp 컴파일 오류를 해결하기 위해 필요한 시스템 라이브러리를 설치합니다.
RUN apk add --no-cache libc6-compat python3 make g++

# pnpm 설치
RUN npm install -g pnpm

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 인자(build-arg)를 선언합니다.
ARG NEXT_PUBLIC_API_BASE_URL
# 받은 빌드 인자를 환경 변수로 설정합니다.
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}

# 의존성 파일 복사
COPY package.json pnpm-lock.yaml* ./

# 의존성 설치
RUN pnpm install --frozen-lockfile

# 소스 코드 복사
COPY . .

# 애플리케이션 빌드 (이때 위의 ENV가 사용됩니다)
RUN pnpm run build

# 2. 프로덕션 환경 설정
FROM node:18-alpine

# pnpm 설치
RUN npm install -g pnpm

WORKDIR /app

# 프로덕션 환경에 필요한 환경 변수 설정
ENV NODE_ENV=production

# 빌드 결과물 및 필요 파일 복사
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# 애플리케이션 실행
CMD ["pnpm", "start"]
