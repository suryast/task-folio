/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode
  reactStrictMode: true,
  
  // Static export for Cloudflare Pages
  output: 'export',
  
  // Disable image optimization
  images: {
    unoptimized: true,
  },
  
  // Trailing slashes for static hosting
  trailingSlash: true,
}

export default nextConfig
