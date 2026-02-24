import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Star, Phone, Mail } from 'lucide-react';
import { useStaffList, Staff } from '@salon-flow/shared';
import { Button, Card, CardContent, Input, Avatar, Badge } from '@salon-flow/ui';

const StaffPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: staffList, isLoading } = useStaffList();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredStaff = (staffList || []).filter((member: Staff) =>
    (member.name || `${member.firstName} ${member.lastName}`).toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'owner': return 'default';
      case 'manager': return 'success';
      case 'senior_stylist': return 'warning';
      case 'stylist': return 'secondary';
      default: return 'outline';
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Staff</h1>
        <Button onClick={() => navigate('/staff/new')}>
          <Plus className="w-4 h-4 mr-2" />
          Add Staff
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <Input
          placeholder="Search staff..."
          className="pl-10"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Staff Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredStaff.map((member: Staff) => (
          <Card
            key={member.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => navigate(`/staff/${member.id}`)}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <Avatar
                  src={member.photoURL}
                  alt={member.name || `${member.firstName} ${member.lastName}`}
                  size="lg"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {member.name || `${member.firstName} ${member.lastName}`}
                    </h3>
                    <Badge variant={member.isActive ? 'success' : 'secondary'}>
                      {member.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <Badge variant={getRoleBadgeVariant(member.role)} className="mt-1">
                    {member.role.replace('_', ' ').replace(/\w/g, l => l.toUpperCase())}
                  </Badge>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Mail className="w-3 h-3" />
                      <span className="truncate">{member.email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Phone className="w-3 h-3" />
                      <span>{member.phone}</span>
                    </div>
                  </div>
                  {member.rating !== undefined && (
                    <div className="flex items-center gap-1 mt-2">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-medium">{member.rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredStaff.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No staff members found</p>
        </div>
      )}
    </div>
  );
};

export default StaffPage;
