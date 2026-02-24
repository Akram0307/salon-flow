import { WifiOff, RefreshCw } from 'lucide-react';
import { Button } from '@/components/atoms/Button';

export function OfflinePage() {
  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-50">
      <div className="text-center max-w-md">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
            <WifiOff className="w-10 h-10 text-gray-500" />
          </div>
        </div>
        
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          You're offline
        </h1>
        
        <p className="text-gray-600 mb-6">
          It looks like you've lost your internet connection. 
          Please check your connection and try again.
        </p>
        
        <div className="space-y-3">
          <Button
            variant="primary"
            onClick={handleRetry}
            className="w-full gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </Button>
          
          <p className="text-sm text-gray-500">
            Some features may be available offline. 
            Check your cached data below.
          </p>
        </div>
        
        <div className="mt-8 p-4 bg-white rounded-lg border border-gray-200">
          <h3 className="font-medium text-gray-900 mb-2">Available Offline</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• View cached bookings</li>
            <li>• Access customer list</li>
            <li>• View staff schedule</li>
            <li>• Read analytics (last synced)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
