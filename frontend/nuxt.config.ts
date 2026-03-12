export default defineNuxtConfig({
  ssr: true,
  devServer: {
    port: 3003
  },
  vite: {
    server: {
      allowedHosts: ['aimsb.ddnsfree.com']
    }
  },
  components: [
    {
      path: '~/components',
      pathPrefix: false
    }
  ],
  css: [
    '@/assets/styles/tokens.css',
    '@/assets/styles/theme.css',
    '@/assets/styles/admin.css',
    '@/assets/styles/user.css',
    '@/assets/styles/toast.css'
  ],
  modules: [],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:1111'
    }
  },
  app: {
    head: {
      title: 'NEU Data Query System',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  }
});
