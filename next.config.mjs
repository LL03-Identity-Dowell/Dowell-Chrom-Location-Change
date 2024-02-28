/** @type {import('next').NextConfig} */
const nextConfig = {
    output:'export',
    basePath: process.env.NODE_ENV === 'production' ? '/Dowell-Chrome-Location-Change' : '',
    assetPrefix: process.env.NODE_ENV === 'production' ? '/Dowell-Chrome-Location-Change/' : '',
  };
  /* module.exports = nextConfig*/
  export default nextConfig;
  