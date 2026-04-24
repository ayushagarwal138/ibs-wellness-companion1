'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  Shield, 
  Trash2, 
  Lock,
  Download,
  UserX,
  X
} from 'lucide-react';
import { useAuth } from '@/contexts/auth-context';
import { toast } from 'react-hot-toast';

interface AccountManagementProps {
  className?: string;
}

// Simple Modal Component
const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}> = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="relative bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
        {children}
      </div>
    </div>
  );
};

export const AccountManagement: React.FC<AccountManagementProps> = ({ 
  className = '' 
}) => {
  const { user, logout, deleteAccount } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [deleteCountdown, setDeleteCountdown] = useState(0);

  // Countdown timer for delete button
  React.useEffect(() => {
    if (showDeleteModal && deleteCountdown > 0) {
      const timer = setTimeout(() => {
        setDeleteCountdown(deleteCountdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [showDeleteModal, deleteCountdown]);

  // Start countdown when modal opens
  React.useEffect(() => {
    if (showDeleteModal) {
      setDeleteCountdown(5); // 5 second countdown
    }
  }, [showDeleteModal]);

  const handleDeleteAccount = async () => {
    if (confirmationText !== 'DELETE MY ACCOUNT') {
      toast.error('Please type "DELETE MY ACCOUNT" to confirm account deletion');
      return;
    }

    try {
      setIsDeleting(true);
      
      // Show a warning toast before proceeding
      toast.loading('Deleting your account...', { duration: 2000 });
      
      // Call the actual account deletion function from auth context
      await deleteAccount();
      
      setShowDeleteModal(false);
      
      // Success message is handled in the auth context
      
    } catch (error: any) {
      console.error('Account deletion error:', error);
      
      // Provide specific error messages based on error type
      if (error.message?.includes('Network')) {
        toast.error('Network error. Please check your connection and try again.');
      } else if (error.message?.includes('Unauthorized')) {
        toast.error('Session expired. Please log in again and try deleting your account.');
      } else if (error.message?.includes('Server')) {
        toast.error('Server error. Please try again later or contact support.');
      } else {
        toast.error(error.message || 'Failed to delete account. Please try again or contact support.');
      }
    } finally {
      setIsDeleting(false);
    }
  };

  const handleExportData = async () => {
    setIsExporting(true);
    try {
      const response = await fetch('/api/v1/users/export-data', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to export data');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `ibs-wellness-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast.success('Data exported successfully');
    } catch (error) {
      console.error('Error exporting data:', error);
      toast.error('Failed to export data. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const closeDeleteModal = () => {
    setShowDeleteModal(false);
    setConfirmationText('');
    setDeleteCountdown(0);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Privacy & Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Privacy & Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium">Two-Factor Authentication</h4>
              <p className="text-sm text-muted-foreground">
                Add an extra layer of security to your account
              </p>
            </div>
            <Badge variant="outline">Coming Soon</Badge>
          </div>
          
          <div className="border-t pt-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">Login Sessions</h4>
                <p className="text-sm text-muted-foreground">
                  Manage your active login sessions
                </p>
              </div>
              <Button variant="outline" size="sm" disabled>
                <Lock className="h-4 w-4 mr-2" />
                Manage Sessions
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Management */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Data Management
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium">Export Your Data</h4>
              <p className="text-sm text-muted-foreground">
                Download a copy of all your health data and preferences
              </p>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleExportData}
              disabled={isExporting}
            >
              <Download className="h-4 w-4 mr-2" />
              {isExporting ? 'Exporting...' : 'Export Data'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200 bg-red-50/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-700">
            <AlertTriangle className="h-5 w-5" />
            Danger Zone
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-red-100 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <UserX className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-red-800 mb-2">
                  Delete Account
                </h4>
                <p className="text-sm text-red-700 mb-4">
                  Permanently delete your account and all associated data. This action cannot be undone.
                </p>
                
                <div className="bg-white border border-red-200 rounded-md p-3 mb-4">
                  <h5 className="font-medium text-red-800 mb-2">
                    What will be deleted:
                  </h5>
                  <ul className="text-sm text-red-700 space-y-1">
                    <li>• Your profile and personal information</li>
                    <li>• All symptom and diet logs</li>
                    <li>• ML predictions and analytics</li>
                    <li>• Chat history and recommendations</li>
                    <li>• Subscription and payment information</li>
                    <li>• All other associated data</li>
                  </ul>
                </div>

                <Button 
                  variant="destructive" 
                  size="sm"
                  onClick={() => setShowDeleteModal(true)}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Account
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={showDeleteModal} onClose={closeDeleteModal}>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-red-600 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Delete Account
            </h3>
            <button
              onClick={closeDeleteModal}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-red-800 mb-2">
                    ⚠️ PERMANENT ACTION - CANNOT BE UNDONE
                  </h4>
                  <p className="text-sm text-red-700 mb-2">
                    This will permanently delete your account and ALL associated data including:
                  </p>
                  <ul className="text-sm text-red-700 list-disc list-inside space-y-1">
                    <li>Your profile and personal information</li>
                    <li>All symptom logs and health data</li>
                    <li>Diet logs and nutrition tracking</li>
                    <li>ML predictions and insights</li>
                    <li>Chat history and conversations</li>
                    <li>Subscription and billing information</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <p className="text-sm text-gray-600 font-medium">
              If you're sure you want to proceed, type "DELETE MY ACCOUNT" below:
            </p>
            
            <div>
              <Label htmlFor="confirmation" className="text-sm font-medium">
                Confirmation Text:
              </Label>
              <Input
                id="confirmation"
                value={confirmationText}
                onChange={(e) => setConfirmationText(e.target.value)}
                placeholder="DELETE MY ACCOUNT"
                className="mt-1"
                disabled={isDeleting}
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 mt-6">
            <Button
              variant="outline"
              onClick={closeDeleteModal}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteAccount}
              disabled={
                confirmationText !== 'DELETE MY ACCOUNT' || 
                isDeleting || 
                deleteCountdown > 0
              }
            >
              {isDeleting 
                ? 'Deleting...' 
                : deleteCountdown > 0 
                  ? `Wait ${deleteCountdown}s` 
                  : 'Delete Account'
              }
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AccountManagement;