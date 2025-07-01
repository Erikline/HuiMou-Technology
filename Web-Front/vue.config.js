const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true, 
  lintOnSave: false,
  devServer: {
    proxy: {
      '/processed_images': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})