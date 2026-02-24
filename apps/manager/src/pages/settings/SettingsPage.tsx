import React from 'react';
import { Card, CardContent } from '@salon-flow/ui';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      <Card>
        <CardContent className="p-6">
          <p className="text-gray-500">Settings will be displayed here</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPage;
