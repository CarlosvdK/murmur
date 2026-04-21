/** @type {import('next').NextConfig} */
const nextConfig = {
  onDemandEntries: {
    maxInactiveAge: 60 * 60 * 1000,
    pagesBufferLength: 10,
  },
  // Linting and type-checking happen in CI (see .github/workflows/test.yml).
  // Letting `next build` fail on them blocks production deploys for issues
  // that are entirely in test files -- not worth it.
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
