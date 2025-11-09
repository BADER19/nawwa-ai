FROM node:20-alpine

WORKDIR /app
COPY package.json package-lock.json* /app/
RUN npm install --no-audit --no-fund || true
COPY . /app

# Build the Next.js production bundle
RUN npm run build

# Use port 8080 for Railway
EXPOSE 8080
ENV PORT=8080

# Start production server
CMD ["npm", "run", "start"]

