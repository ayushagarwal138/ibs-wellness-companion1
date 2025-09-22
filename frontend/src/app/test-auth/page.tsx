'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { apiService } from '@/lib/api';

export default function TestAuthPage() {
  const { user, login, logout } = useAuth();
  const [email, setEmail] = useState('test@test.com');
  const [password, setPassword] = useState('test12345');
  const [dietLogs, setDietLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      setDietLogs([]);
    } catch (err: any) {
      setError(err.message || 'Logout failed');
    }
  };

  const fetchDietLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await apiService.getDietLogs();
      setDietLogs(response.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch diet logs');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Authentication & Diet Logs Test</h1>
        
        {/* Authentication Status */}
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          {user ? (
            <div>
              <p className="text-green-600 mb-2">✅ Logged in as: {user.email}</p>
              <p className="text-sm text-gray-600 mb-4">User ID: {user.id}</p>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          ) : (
            <div>
              <p className="text-red-600 mb-4">❌ Not logged in</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Email:</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full p-2 border rounded"
                    placeholder="john.doe@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Password:</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full p-2 border rounded"
                    placeholder="password123"
                  />
                </div>
                <button
                  onClick={handleLogin}
                  disabled={loading}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  {loading ? 'Logging in...' : 'Login'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Diet Logs Test */}
        {user && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Diet Logs Test</h2>
            <button
              onClick={fetchDietLogs}
              disabled={loading}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50 mb-4"
            >
              {loading ? 'Loading...' : 'Fetch Diet Logs'}
            </button>

            {dietLogs.length > 0 ? (
              <div>
                <p className="text-green-600 mb-4">✅ Found {dietLogs.length} diet logs</p>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {dietLogs.map((log, index) => (
                    <div key={index} className="border p-4 rounded">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium">{log.meal_type || 'Unknown meal'}</span>
                        <span className="text-sm text-gray-500">
                          {log.created_at ? new Date(log.created_at).toLocaleDateString() : 'No date'}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        <p>Foods: {log.foods?.join(', ') || 'No foods listed'}</p>
                        <p>Calories: {log.calories || 'N/A'}</p>
                        {log.notes && <p>Notes: {log.notes}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No diet logs found or not fetched yet.</p>
            )}
          </div>
        )}

        {/* Local Storage Debug */}
        <div className="bg-white p-6 rounded-lg shadow mt-6">
          <h2 className="text-xl font-semibold mb-4">Local Storage Debug</h2>
          <div className="text-sm font-mono">
            <p>Access Token: {typeof window !== 'undefined' ? localStorage.getItem('access_token') ? '✅ Present' : '❌ Missing' : 'Loading...'}</p>
            <p>Refresh Token: {typeof window !== 'undefined' ? localStorage.getItem('refresh_token') ? '✅ Present' : '❌ Missing' : 'Loading...'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}