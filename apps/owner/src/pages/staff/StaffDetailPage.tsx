import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Edit, Mail, Phone, Star, TrendingUp, DollarSign, Users } from 'lucide-react';
import { useStaff, useUpdateStaff } from '@salon-flow/shared';
import { Button, Card, CardContent, CardHeader, CardTitle, Avatar, Badge } from '@salon-flow/ui';

const StaffDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: staffMember, isLoading } = useStaff(id || '');
  const updateStaff = useUpdateStaff();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!staffMember) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Staff member not found</h2>
        <Button onClick={() => navigate('/staff')} className="mt-4">Back to Staff</Button>
      </div>
    );
  }

  const handleToggleActive = async () => {
    await updateStaff.mutateAsync({
      id: id || '',
      data: { isActive: !staffMember.isActive },
    });
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'owner': return 'default';
      case 'manager': return 'success';
      case 'senior_stylist': return 'warning';
      case 'stylist': return 'secondary';
      default: return 'outline';
    }
  };

  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/staff')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold text-gray-900">Staff Details</h1>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/staff/${id}/edit`)}>
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" onClick={handleToggleActive}>
            {staffMember.isActive ? 'Deactivate' : 'Activate'}
          </Button>
        </div>
      </div>

      {/* Profile Card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-6">
            <Avatar
              src={staffMember.photoURL}
              alt={staffMember.name || `${staffMember.firstName} ${staffMember.lastName}`}
              size="xl"
            />
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-semibold text-gray-900">
                  {staffMember.name || `${staffMember.firstName} ${staffMember.lastName}`}
                </h2>
                <Badge variant={staffMember.isActive ? 'success' : 'secondary'}>
                  {staffMember.isActive ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <Badge variant={getRoleBadgeVariant(staffMember.role)} className="mt-2">
                {staffMember.role.replace('_', ' ').replace(/\w/g, l => l.toUpperCase())}
              </Badge>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span>{staffMember.email}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{staffMember.phone}</span>
                </div>
              </div>
              {staffMember.specialization && staffMember.specialization.length > 0 && (
                <div className="mt-4">
                  <span className="text-sm text-gray-500">Specializations: </span>
                  {staffMember.specialization.map((s: any, i: any) => (
                    <Badge key={i} variant="outline" className="mr-1">{s}</Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Bookings</p>
                <p className="text-xl font-semibold">{staffMember.totalBookings || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <DollarSign className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Revenue</p>
                <p className="text-xl font-semibold">₹{(staffMember.totalRevenue || 0).toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Star className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Rating</p>
                <p className="text-xl font-semibold">{staffMember.rating?.toFixed(1) || 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Completion Rate</p>
                <p className="text-xl font-semibold">{staffMember.completionRate ? `${staffMember.completionRate}%` : 'N/A'}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schedule */}
      <Card>
        <CardHeader>
          <CardTitle>Weekly Schedule</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {staffMember.schedule?.map((slot: any, index: any) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{days[slot.dayOfWeek]}</span>
                {slot.isWorking ? (
                  <span className="text-gray-600">
                    {slot.startTime} - {slot.endTime}
                  </span>
                ) : (
                  <Badge variant="secondary">Off</Badge>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StaffDetailPage;
