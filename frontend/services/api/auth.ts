import type {
  ForgotPasswordPayload,
  ForgotPasswordResponse,
  LoginPayload,
  LoginResponse,
  ResetPasswordPayload,
  ResetPasswordResponse
} from '@/types/auth';
import { useApiFetch } from '@/services/api/client';

export const login = async (payload: LoginPayload) => {
  const api = useApiFetch();
  return await api<LoginResponse>('/auth/login', {
    method: 'POST',
    body: payload
  });
};

export const forgotPassword = async (payload: ForgotPasswordPayload) => {
  const api = useApiFetch();
  return await api<ForgotPasswordResponse>('/auth/forgot-password', {
    method: 'POST',
    body: payload
  });
};

export const resetPassword = async (payload: ResetPasswordPayload) => {
  const api = useApiFetch();
  return await api<ResetPasswordResponse>('/auth/reset-password', {
    method: 'POST',
    body: payload
  });
};
