# syntax=docker/dockerfile:1.6

FROM node:20-bookworm-slim AS builder

ENV PNPM_HOME=/root/.local/share/pnpm \
    NODE_ENV=production

RUN corepack enable pnpm

WORKDIR /workspace

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY apps/frontend ./apps/frontend

RUN pnpm install --frozen-lockfile --filter legal-discovery-frontend...
RUN pnpm --filter legal-discovery-frontend build

FROM gcr.io/distroless/nodejs20-debian12

ENV NODE_ENV=production \
    FRONTEND_PORT=4173 \
    FRONTEND_HOST=0.0.0.0

WORKDIR /srv/app

COPY --from=builder /workspace/apps/frontend/dist ./dist
COPY apps/frontend/server.mjs ./server.mjs

EXPOSE 4173

USER nonroot

ENTRYPOINT ["node", "server.mjs"]
