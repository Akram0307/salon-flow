import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Lock, Eye, EyeOff, User, Phone, Loader2 } from 'lucide-react';
import { useAuthStore } from '@/stores';
import { api } from '@salon-flow/shared';
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@salon-flow/ui';
import { registerFormSchema, type RegisterFormData } from '@salon-flow/shared';
import type { User as AuthUser } from '@salon-flow/shared';

interface RegisterResponse {
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

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading: authLoading, error: storeError, clearError } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerFormSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      clearError();
      
      // Call backend register API directly
      const response = await api.post<RegisterResponse>('/auth/register', {
        email: data.email,
        password: data.password,
        name: `${data.firstName} ${data.lastName}`,
      });

      const { access_token, user: apiUser } = response;

      // Map API response to User type
      const user: AuthUser = {
        uid: apiUser.id,
        email: apiUser.email,
        displayName: apiUser.name,
        photoURL: apiUser.photo_url,
        role: apiUser.role as any,
        salonId: apiUser.salon_id,
      };

      // Update useAuthStore - single source of truth
      login(user, access_token);

      navigate('/dashboard');
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Registration failed';
      setError(message);
    }
  };

  const isLoading = isSubmitting || authLoading;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Create your salon</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {(error || storeError) && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">{error || storeError}</div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">First Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input {...register('firstName')} placeholder="John" className="pl-10" />
                </div>
                {errors.firstName && <p className="text-red-500 text-sm">{errors.firstName.message}</p>}
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">Last Name</label>
                <Input {...register('lastName')} placeholder="Doe" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Salon Name</label>
              <Input {...register('salonName')} placeholder="My Salon" />
              {errors.salonName && <p className="text-red-500 text-sm">{errors.salonName.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input {...register('email')} type="email" placeholder="you@example.com" className="pl-10" />
              </div>
              {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Phone</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input {...register('phone')} type="tel" placeholder="9876543210" className="pl-10" />
              </div>
              {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  className="pl-10 pr-10"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2">
                  {showPassword ? <EyeOff className="h-5 w-5 text-gray-400" /> : <Eye className="h-5 w-5 text-gray-400" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-sm">{errors.password.message}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create Account'}
            </Button>

            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:underline">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default RegisterPage;
