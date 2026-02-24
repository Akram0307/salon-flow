import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock, Eye, EyeOff, Loader2, Sparkles } from 'lucide-react';
import { useAuthStore } from '@/stores';
import { api } from '@salon-flow/shared';
import { Button, Input, Card } from '@/components/atoms';
import { loginFormSchema, type LoginFormData } from '@salon-flow/shared';
import type { User } from '@salon-flow/shared';

interface LoginResponse {
  access_token: string;
  user: {
    id: string;
    email: string;
    name?: string;
    photo_url?: string;
    role?: string;
    salon_id?: string;
    [key: string]: unknown;
  };
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const returnUrl = searchParams.get('returnUrl');
  
  // Use useAuthStore as single source of truth
  const { login, isLoading: authLoading, error: storeError, clearError } = useAuthStore();
  
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginFormSchema),
  });

  // Clear errors on mount
  useEffect(() => {
    clearError();
    setError(null);
  }, [clearError]);

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      clearError();
      
      // Call backend login API directly
      const response = await api.post<LoginResponse>('/auth/login', {
        email: data.email,
        password: data.password,
      });

      const { access_token, user: apiUser } = response;

      // Map API response to User type
      const user: User = {
        uid: apiUser.id,
        email: apiUser.email,
        displayName: apiUser.name,
        photoURL: apiUser.photo_url,
        role: apiUser.role as any,
        salonId: apiUser.salon_id,
      };

      // Update useAuthStore - single source of truth
      login(user, access_token);

      // Navigate to return URL or dashboard
      navigate(returnUrl ? decodeURIComponent(returnUrl) : '/dashboard');
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Login failed. Please try again.';
      setError(message);
    }
  };

  // Google Sign-in temporarily disabled - Firebase removed
  // TODO: Implement backend-based Google OAuth when needed
  /*
  const handleGoogleSignIn = async () => {
    try {
      setIsGoogleLoading(true);
      setError(null);
      
      const provider = new GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');
      
      const auth = getAuth();
      const result = await signInWithPopup(auth, provider);
      
      // Get Firebase ID token
      const idToken = await result.user.getIdToken();
      
      // Store token and update auth state via useAuthStore
      const user: User = {
        uid: result.user.uid,
        email: result.user.email || '',
        displayName: result.user.displayName || undefined,
        photoURL: result.user.photoURL || undefined,
      };
      
      // Update useAuthStore directly
      const { setTokens, setUser } = useAuthStore.getState();
      setTokens(idToken);
      setUser(user);
      
      // Navigate to return URL or dashboard
      navigate(returnUrl ? decodeURIComponent(returnUrl) : '/dashboard');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Google sign-in failed. Please try again.';
      setError(message);
    } finally {
      setIsGoogleLoading(false);
    }
  };
  */

  const isLoading = isSubmitting || authLoading;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Logo Section */}
      <div className="mb-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-600 shadow-lg mb-4">
          <Sparkles className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Salon Flow</h1>
        <p className="mt-2 text-sm text-gray-600">AI-Powered Salon Management</p>
      </div>

      <Card className="w-full max-w-md p-8 shadow-xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Welcome back</h2>
          <p className="mt-1 text-sm text-gray-600">Sign in to manage your salon</p>
        </div>

        {/* Error Display */}
        {(error || storeError) && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200">
            <p className="text-sm text-red-600">{error || storeError}</p>
          </div>
        )}

        {/* Google Sign In - Temporarily Disabled */}
        {/*
        <Button
          type="button"
          variant="outline"
          className="w-full mb-4 flex items-center justify-center gap-2"
          onClick={handleGoogleSignIn}
          disabled={isLoading}
        >
          {isGoogleLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Chrome className="w-5 h-5 text-red-500" />
          )}
          Continue with Google
        </Button>
        */}

        {/* Divider - Hidden since Google Sign-in is disabled */}
        {/*
        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with email</span>
          </div>
        </div>
        */}

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" data-testid="login-form">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                {...register('email')}
                type="email"
                placeholder="you@example.com"
                className="pl-10"
                disabled={isLoading}
                data-testid="email-input"
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                {...register('password')}
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="pl-10 pr-10"
                disabled={isLoading}
                data-testid="password-input"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                disabled={isLoading}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center">
              <input type="checkbox" className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              <span className="ml-2 text-gray-600">Remember me</span>
            </label>
            <Link to="/forgot-password" className="text-indigo-600 hover:text-indigo-500 font-medium">
              Forgot password?
            </Link>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
            data-testid="login-button"
          >
            {isSubmitting || authLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Signing in...
              </>
            ) : (
              'Sign in'
            )}
          </Button>
        </form>

        {/* Sign Up Link */}
        <p className="mt-6 text-center text-sm text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-600 hover:text-indigo-500 font-medium">
            Create one now
          </Link>
        </p>
      </Card>

      {/* Footer */}
      <p className="mt-8 text-center text-xs text-gray-500">
        By signing in, you agree to our{' '}
        <Link to="/terms" className="text-indigo-600 hover:underline">Terms of Service</Link>
        {' '}and{' '}
        <Link to="/privacy" className="text-indigo-600 hover:underline">Privacy Policy</Link>
      </p>
    </div>
  );
};

export default LoginPage;
