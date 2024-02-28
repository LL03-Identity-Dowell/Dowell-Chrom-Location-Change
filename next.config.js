module.exports = {
    // Other configuration options
    target: 'serverless',
    exportPathMap: function () {
      return {
        '/': { page: '/' },
        // Add other routes if needed
      };
    },
  };
  