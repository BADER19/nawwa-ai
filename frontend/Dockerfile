FROM node:20-alpine

WORKDIR /app
COPY package.json package-lock.json* /app/
RUN npm install --no-audit --no-fund || true
COPY . /app
EXPOSE 3000
CMD ["npm", "run", "dev"]

