FROM node:20-slim

WORKDIR /app

# Copy package files first
COPY package.json ./

# Install only production runtime dependencies + typescript for config
RUN npm install --omit=dev && npm install typescript

# Copy pre-built output, public assets and required config files
COPY .next ./.next
COPY public ./public
COPY next.config.js ./
COPY next-env.d.ts ./
COPY .env.production ./.env.production

EXPOSE 3002

CMD ["npx", "next", "start", "-p", "3002"]
