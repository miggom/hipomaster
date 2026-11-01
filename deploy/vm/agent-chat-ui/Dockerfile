# Agent Chat UI (LangChain) con commit fijado. Ver docs/DESPLIEGUE.md §4.5.
FROM node:20-alpine AS build
ARG AGENT_CHAT_UI_REF=main
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_ASSISTANT_ID=hipomaster
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_ASSISTANT_ID=$NEXT_PUBLIC_ASSISTANT_ID \
    NEXT_TELEMETRY_DISABLED=1
RUN apk add --no-cache git && corepack enable
WORKDIR /app
RUN git clone https://github.com/langchain-ai/agent-chat-ui.git . && git checkout "$AGENT_CHAT_UI_REF"
RUN pnpm install --frozen-lockfile && pnpm build

FROM node:20-alpine
RUN corepack enable
WORKDIR /app
COPY --from=build /app /app
ENV NODE_ENV=production PORT=3000 NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000
USER node
CMD ["pnpm", "start"]
