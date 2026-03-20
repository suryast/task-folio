/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode
  reactStrictMode: true,
  
  // Disable image optimization for Cloudflare Pages
  images: {
    unoptimized: true,
  },
}

export default nextConfig
