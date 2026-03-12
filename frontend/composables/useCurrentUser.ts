type CurrentUser = {
  id: number;
  username: string;
  full_name: string;
  role: string;
  permissions?: string[];
};

export const useCurrentUser = () => {
  const user = useState<CurrentUser | null>('current-user', () => null);

  const load = () => {
    if (process.client && !user.value) {
      const raw = localStorage.getItem('neu_user');
      if (raw) {
        user.value = JSON.parse(raw);
      }
    }
  };

  const save = (data: CurrentUser) => {
    user.value = data;
    if (process.client) {
      localStorage.setItem('neu_user', JSON.stringify(data));
    }
  };

  const clear = () => {
    user.value = null;
    if (process.client) {
      localStorage.removeItem('neu_user');
    }
  };

  return { user, load, save, clear };
};
