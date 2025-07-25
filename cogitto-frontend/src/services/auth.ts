import api from '@/lib/api';
import { AuthTokens, LoginRequest, RegisterRequest, User } from '@/types';

export const authService = {
  // Register new user
  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post('/auth/register', {
      email: userData.email,
      password: userData.password,
      full_name: userData.fullName,
      phone_number: userData.phoneNumber || undefined,
    });
    return response.data;
  },

  // Login user
  async login(credentials: LoginRequest): Promise<AuthTokens> {
    const response = await api.post('/auth/login', credentials);
    
    // Store tokens in localStorage
    localStorage.setItem('cogitto_access_token', response.data.access_token);
    localStorage.setItem('cogitto_refresh_token', response.data.refresh_token);
    localStorage.setItem('cogitto_user', JSON.stringify(response.data.user));
    
    return response.data;
  },

  // Logout user
  logout() {
    localStorage.removeItem('cogitto_access_token');
    localStorage.removeItem('cogitto_refresh_token');
    localStorage.removeItem('cogitto_user');
  },

  // Get current user from localStorage
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('cogitto_user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('cogitto_access_token');
  },
};
