FROM node:22-alpine

WORKDIR /app
ENV BACKEND_URL=http://api:8000
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
