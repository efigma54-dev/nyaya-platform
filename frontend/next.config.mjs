import { dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Silence the "multiple lockfiles" workspace-root warning
  outputFileTracingRoot: __dirname,

  async rewrites() {
    const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },

  async redirects() {
    return [];
  },
};

export default nextConfig;
