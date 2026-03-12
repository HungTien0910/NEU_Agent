export type LoginPayload = {
  username: string;
  password: string;
};

export type UserPublic = {
  id: number;
  username: string;
  full_name: string;
  role: 'admin' | 'user';
  permissions: string[];
  is_active: boolean;
};

export type LoginResponse = {
  access_token: string;
  token_type: 'bearer';
  user: UserPublic;
};

export type ForgotPasswordPayload = {
  username: string;
};

export type ForgotPasswordResponse = {
  message: string;
};

export type ResetPasswordPayload = {
  token: string;
  new_password: string;
  confirm_password: string;
};

export type ResetPasswordResponse = {
  message: string;
};
