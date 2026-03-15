/** @type {import('next').NextConfig} */
module.exports = {
  async rewrites() {
    const apiDest = process.env.INTERNAL_API_URL || "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${apiDest}/:path*` }];
  },
};
