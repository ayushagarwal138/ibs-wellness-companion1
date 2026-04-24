'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'react-hot-toast';
import { 
  FileText, 
  Plus, 
  Edit, 
  Eye,
  Download,
  CheckCircle,
  AlertCircle,
  Clock,
  DollarSign,
  Calendar,
  Filter,
  Search
} from 'lucide-react';

interface Invoice {
  id: string;
  invoice_number: string;
  amount: number;
  tax_amount?: number;
  total_amount: number;
  status: string;
  due_date: string;
  issue_date: string;
  description?: string;
  created_at: string;
}

interface InvoiceCreate {
  invoice_number: string;
  amount: number;
  tax_amount?: number;
  due_date: string;
  issue_date: string;
  description?: string;
}

export const Invoices: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [filteredInvoices, setFilteredInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState<InvoiceCreate>({
    invoice_number: '',
    amount: 0,
    issue_date: new Date().toISOString().split('T')[0] || '',
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] || '',
    description: ''
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  useEffect(() => {
    filterInvoices();
  }, [invoices, statusFilter, searchTerm]);

  const fetchInvoices = async () => {
    try {
      const url = statusFilter 
        ? `/api/v1/financial/invoices?status=${statusFilter}`
        : '/api/v1/financial/invoices';
        
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInvoices(data);
      } else {
        toast.error('Failed to fetch invoices');
      }
    } catch (error) {
      toast.error('Error fetching invoices');
    } finally {
      setLoading(false);
    }
  };

  const filterInvoices = () => {
    let filtered = invoices;

    if (statusFilter) {
      filtered = filtered.filter(invoice => invoice.status === statusFilter);
    }

    if (searchTerm) {
      filtered = filtered.filter(invoice => 
        invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        invoice.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredInvoices(filtered);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingId 
        ? `/api/v1/financial/invoices/${editingId}`
        : '/api/v1/financial/invoices';
      
      const method = editingId ? 'PUT' : 'POST';
      
      // Calculate total amount
      const totalAmount = formData.amount + (formData.tax_amount || 0);
      const submitData = {
        ...formData,
        total_amount: totalAmount
      };
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(submitData)
      });

      if (response.ok) {
        toast.success(editingId ? 'Invoice updated' : 'Invoice created');
        setShowAddForm(false);
        setEditingId(null);
        resetForm();
        fetchInvoices();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save invoice');
      }
    } catch (error) {
      toast.error('Error saving invoice');
    }
  };

  const handleStatusUpdate = async (id: string, status: string) => {
    try {
      const response = await fetch(`/api/v1/financial/invoices/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        toast.success('Invoice status updated');
        fetchInvoices();
      } else {
        toast.error('Failed to update invoice status');
      }
    } catch (error) {
      toast.error('Error updating invoice status');
    }
  };

  const startEdit = (invoice: Invoice) => {
    setEditingId(invoice.id);
    setFormData({
      invoice_number: invoice.invoice_number,
      amount: invoice.amount,
      tax_amount: invoice.tax_amount,
      issue_date: invoice.issue_date,
      due_date: invoice.due_date,
      description: invoice.description || ''
    });
    setShowAddForm(true);
  };

  const resetForm = () => {
    setFormData({
      invoice_number: '',
      amount: 0,
      issue_date: new Date().toISOString().split('T')[0] || '',
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] || '',
      description: ''
    });
    setEditingId(null);
    setShowAddForm(false);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { color: 'bg-gray-100 text-gray-800', icon: FileText },
      sent: { color: 'bg-blue-100 text-blue-800', icon: Clock },
      paid: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      overdue: { color: 'bg-red-100 text-red-800', icon: AlertCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: AlertCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon size={12} />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const generateInvoiceNumber = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `INV-${year}${month}-${random}`;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center">Loading invoices...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Invoices</h2>
        <Button 
          onClick={() => {
            setFormData({
              ...formData,
              invoice_number: generateInvoiceNumber()
            });
            setShowAddForm(true);
          }}
          className="flex items-center gap-2"
        >
          <Plus size={16} />
          Create Invoice
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <Input
                  placeholder="Search invoices..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="w-full md:w-48">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Statuses</SelectItem>
                  <SelectItem value="draft">Draft</SelectItem>
                  <SelectItem value="sent">Sent</SelectItem>
                  <SelectItem value="paid">Paid</SelectItem>
                  <SelectItem value="overdue">Overdue</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Add/Edit Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>
              {editingId ? 'Edit Invoice' : 'Create Invoice'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="invoice_number">Invoice Number</Label>
                  <Input
                    id="invoice_number"
                    placeholder="INV-2024-001"
                    value={formData.invoice_number}
                    onChange={(e) => setFormData({...formData, invoice_number: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="amount">Amount (₹)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    placeholder="1000.00"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="tax_amount">Tax Amount (₹)</Label>
                  <Input
                    id="tax_amount"
                    type="number"
                    step="0.01"
                    placeholder="180.00"
                    value={formData.tax_amount || ''}
                    onChange={(e) => setFormData({...formData, tax_amount: e.target.value ? parseFloat(e.target.value) : undefined})}
                  />
                </div>

                <div>
                  <Label htmlFor="issue_date">Issue Date</Label>
                  <Input
                    id="issue_date"
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => setFormData({...formData, issue_date: e.target.value})}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="due_date">Due Date</Label>
                  <Input
                    id="due_date"
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Invoice description..."
                  value={formData.description || ''}
                  onChange={(e) => setFormData({...formData, description: e.target.value || undefined})}
                  rows={3}
                />
              </div>

              {(formData.amount > 0 || formData.tax_amount) && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span>Total Amount:</span>
                    <span className="font-semibold">
                      {formatCurrency(formData.amount + (formData.tax_amount || 0))}
                    </span>
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <Button type="submit">
                  {editingId ? 'Update' : 'Create'} Invoice
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Invoice Details Modal */}
      {selectedInvoice && (
        <Card className="fixed inset-0 z-50 bg-white m-4 overflow-auto">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Invoice Details</CardTitle>
            <Button variant="outline" onClick={() => setSelectedInvoice(null)}>
              Close
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Invoice Number</Label>
                  <p className="font-medium">{selectedInvoice.invoice_number}</p>
                </div>
                <div>
                  <Label>Status</Label>
                  <div className="mt-1">{getStatusBadge(selectedInvoice.status)}</div>
                </div>
                <div>
                  <Label>Amount</Label>
                  <p className="font-medium">{formatCurrency(selectedInvoice.amount)}</p>
                </div>
                <div>
                  <Label>Total Amount</Label>
                  <p className="font-medium">{formatCurrency(selectedInvoice.total_amount)}</p>
                </div>
                <div>
                  <Label>Issue Date</Label>
                  <p>{new Date(selectedInvoice.issue_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <Label>Due Date</Label>
                  <p>{new Date(selectedInvoice.due_date).toLocaleDateString()}</p>
                </div>
              </div>
              {selectedInvoice.description && (
                <div>
                  <Label>Description</Label>
                  <p className="mt-1">{selectedInvoice.description}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invoices List */}
      <div className="grid gap-4">
        {filteredInvoices.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <FileText className="mx-auto mb-4 text-gray-400" size={48} />
              <p className="text-gray-500">No invoices found</p>
            </CardContent>
          </Card>
        ) : (
          filteredInvoices.map((invoice) => (
            <Card key={invoice.id} className="relative">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">{invoice.invoice_number}</h3>
                      {getStatusBadge(invoice.status)}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-2">
                        <DollarSign size={16} />
                        <span>{formatCurrency(invoice.total_amount)}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Calendar size={16} />
                        <span>Due: {new Date(invoice.due_date).toLocaleDateString()}</span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <Clock size={16} />
                        <span>Created: {new Date(invoice.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {invoice.description && (
                      <p className="mt-2 text-sm text-gray-600 truncate">
                        {invoice.description}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedInvoice(invoice)}
                    >
                      <Eye size={16} />
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => startEdit(invoice)}
                    >
                      <Edit size={16} />
                    </Button>

                    {invoice.status !== 'paid' && invoice.status !== 'cancelled' && (
                      <Select
                        value={invoice.status}
                        onValueChange={(status) => handleStatusUpdate(invoice.id, status)}
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="draft">Draft</SelectItem>
                          <SelectItem value="sent">Sent</SelectItem>
                          <SelectItem value="paid">Paid</SelectItem>
                          <SelectItem value="overdue">Overdue</SelectItem>
                          <SelectItem value="cancelled">Cancelled</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};