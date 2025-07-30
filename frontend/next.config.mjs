/** @type {import('next').NextConfig} */
const nextConfig = {
  // Minimal configuration for development environment
  poweredByHeader: false,
  
  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: true,
  },

  // ESLint configuration
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Skip trailing slash redirect
  skipTrailingSlashRedirect: true,
  
  // Images configuration for development
  images: {
    domains: ['localhost', 'dev.consulting.sa', 'consulting.sa'],
    unoptimized: true,
  },
  
  // Output configuration - simplified for development
  output: 'standalone',
}

export default nextConfig
