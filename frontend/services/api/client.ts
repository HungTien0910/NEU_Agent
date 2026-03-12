export const useApiFetch = () => {
  const config = useRuntimeConfig();

  return $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      if (options.body instanceof FormData) return;
      options.headers = {
        ...(options.headers || {}),
        'Content-Type': 'application/json'
      };
    }
  });
};
