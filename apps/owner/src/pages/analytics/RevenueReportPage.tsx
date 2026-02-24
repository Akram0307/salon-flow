import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@salon-flow/ui';
import { DollarSign, TrendingUp, Calendar } from 'lucide-react';

const RevenueReportPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Revenue Report</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">This Month</p>
                <p className="text-2xl font-bold">₹1,24,500</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Month</p>
                <p className="text-2xl font-bold">₹1,10,800</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Calendar className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">This Year</p>
                <p className="text-2xl font-bold">₹14,85,000</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Table */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Service</th>
                  <th className="text-right py-3 px-4">Bookings</th>
                  <th className="text-right py-3 px-4">Revenue</th>
                  <th className="text-right py-3 px-4">% of Total</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-4">Haircut</td>
                  <td className="text-right py-3 px-4">1,245</td>
                  <td className="text-right py-3 px-4">₹45,000</td>
                  <td className="text-right py-3 px-4">36%</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Hair Color</td>
                  <td className="text-right py-3 px-4">456</td>
                  <td className="text-right py-3 px-4">₹35,500</td>
                  <td className="text-right py-3 px-4">28%</td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Facial</td>
                  <td className="text-right py-3 px-4">389</td>
                  <td className="text-right py-3 px-4">₹28,000</td>
                  <td className="text-right py-3 px-4">22%</td>
                </tr>
                <tr>
                  <td className="py-3 px-4">Other Services</td>
                  <td className="text-right py-3 px-4">858</td>
                  <td className="text-right py-3 px-4">₹16,000</td>
                  <td className="text-right py-3 px-4">14%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RevenueReportPage;
