import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@salon-flow/ui';
import { User, Star, DollarSign } from 'lucide-react';

const StaffPerformancePage: React.FC = () => {
  const staffData = [
    { name: 'Priya Sharma', role: 'Senior Stylist', bookings: 245, revenue: 45000, rating: 4.8 },
    { name: 'Rahul Kumar', role: 'Hair Colorist', bookings: 189, revenue: 38000, rating: 4.7 },
    { name: 'Anita Singh', role: 'Beautician', bookings: 167, revenue: 32000, rating: 4.9 },
    { name: 'Vikram Patel', role: 'Junior Stylist', bookings: 134, revenue: 28000, rating: 4.5 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Staff Performance</h1>
      </div>

      {/* Staff Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {staffData.map((staff, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{staff.name}</CardTitle>
                <Badge variant="secondary">{staff.role}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500 mb-1">
                    <User className="w-4 h-4" />
                    <span className="text-xs">Bookings</span>
                  </div>
                  <p className="text-xl font-bold">{staff.bookings}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500 mb-1">
                    <DollarSign className="w-4 h-4" />
                    <span className="text-xs">Revenue</span>
                  </div>
                  <p className="text-xl font-bold">₹{staff.revenue.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500 mb-1">
                    <Star className="w-4 h-4" />
                    <span className="text-xs">Rating</span>
                  </div>
                  <p className="text-xl font-bold">{staff.rating}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default StaffPerformancePage;
