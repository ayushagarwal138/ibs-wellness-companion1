'use client';

import { signIn } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { FaGoogle, FaGithub } from 'react-icons/fa';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface OAuthButtonsProps {
  callbackUrl?: string;
  className?: string;
}

export function OAuthButtons({ callbackUrl = '/dashboard', className = '' }: OAuthButtonsProps) {
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const router = useRouter();

  const handleOAuthSignIn = async (provider: 'google' | 'github') => {
    try {
      setIsLoading(provider);
      
      const result = await signIn(provider, {
        callbackUrl,
        redirect: false,
      });

      if (result?.error) {
        toast.error(`Failed to sign in with ${provider}. Please try again.`);
      } else if (result?.ok) {
        toast.success(`Successfully signed in with ${provider}!`);
        router.push(callbackUrl);
      }
    } catch (error) {
      console.error(`OAuth ${provider} sign-in error:`, error);
      toast.error(`An error occurred during ${provider} sign-in. Please try again.`);
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={() => handleOAuthSignIn('google')}
        disabled={isLoading !== null}
      >
        {isLoading === 'google' ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
            <span>Signing in...</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <FaGoogle className="h-4 w-4 text-red-500" />
            <span>Continue with Google</span>
          </div>
        )}
      </Button>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        onClick={() => handleOAuthSignIn('github')}
        disabled={isLoading !== null}
      >
        {isLoading === 'github' ? (
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
            <span>Signing in...</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2">
            <FaGithub className="h-4 w-4 text-gray-700" />
            <span>Continue with GitHub</span>
          </div>
        )}
      </Button>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with email
          </span>
        </div>
      </div>
    </div>
  );
}