module.exports = {
  // Other configuration options
  generateStaticParams: async () => {
    return {
      '/': { page: '/' },
      // Add other routes if needed
    };
  },
};
