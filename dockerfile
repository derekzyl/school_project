# 
FROM python:3.11.4
FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 

# Copy package.json and pnpm-lock.yaml
COPY pnpm-lock.yaml package.json ./
# Install app dependencies using PNPM
RUN npm install -g pnpm
# Install dependencies
RUN pnpm i 
# Copy the application code 
COPY . .
# Build the TypeScript code
RUN pnpm run build
# Expose the app
EXPOSE 3000
# Start the application


# 
CMD ["pnpm", "start"]

