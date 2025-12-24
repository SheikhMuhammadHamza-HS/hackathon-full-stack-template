import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  // Creates a minimal server.js with only required dependencies
  // Reduces image size from ~1GB to ~200MB
  output: "standalone",
};

export default nextConfig;
