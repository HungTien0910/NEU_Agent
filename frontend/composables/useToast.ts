type ToastType = 'success' | 'error' | 'info';

export type ToastItem = {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
};

export const useToast = () => {
  const toasts = useState<ToastItem[]>('app-toasts', () => []);

  const push = (message: string, type: ToastType = 'info', duration = 2500) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    toasts.value.push({ id, message, type, duration });
    return id;
  };

  const remove = (id: string) => {
    toasts.value = toasts.value.filter((toast) => toast.id !== id);
  };

  return { toasts, push, remove };
};
