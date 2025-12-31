import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Users, Plus, Phone, Mail, Briefcase, X, Trash2, Edit2 } from 'lucide-react'
import { subConsultantsApi, SubConsultantData } from '../api/client'
import { Button, Badge, ScoreBadge, useToast } from '../components/ui'

interface SubConsultant {
  id: string
  company_name: string
  discipline: string
  tier: 'tier_1' | 'tier_2'
  capacity_status: 'available' | 'limited' | 'unavailable'
  win_rate_together?: number
  past_joint_projects: number
  primary_contact_name?: string
  primary_contact_email?: string
  primary_contact_phone?: string
  typical_fee_range_low?: number
  typical_fee_range_high?: number
  notes?: string
}

const COMMON_DISCIPLINES = [
  'Geotechnical Engineering',
  'Topographic Survey',
  'Archaeological Assessment',
  'Traffic Engineering',
  'Environmental Assessment',
  'Structural Engineering',
  'Landscape Architecture',
  'Hydrogeological Studies',
  'Foundation Engineering',
  'Engineering Materials Testing',
]

export default function SubConsultants() {
  const queryClient = useQueryClient()
  const toast = useToast()
  const [showModal, setShowModal] = useState(false)
  const [editingSub, setEditingSub] = useState<SubConsultant | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['subconsultants'],
    queryFn: () => subConsultantsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: (data: SubConsultantData) => subConsultantsApi.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['subconsultants'] })
      setShowModal(false)
      setEditingSub(null)
      toast.success('Sub-consultant added', `${data.company_name} has been added to your registry.`)
    },
    onError: (error: any) => {
      toast.error('Failed to add sub-consultant', error.response?.data?.detail || 'Please try again.')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: SubConsultantData }) =>
      subConsultantsApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['subconsultants'] })
      setShowModal(false)
      setEditingSub(null)
      toast.success('Sub-consultant updated', `${data.company_name} has been updated.`)
    },
    onError: (error: any) => {
      toast.error('Failed to update', error.response?.data?.detail || 'Please try again.')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => subConsultantsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subconsultants'] })
      setDeleteConfirm(null)
      toast.success('Sub-consultant deleted')
    },
    onError: (error: any) => {
      toast.error('Failed to delete', error.response?.data?.detail || 'Please try again.')
      setDeleteConfirm(null)
    },
  })

  const subs: SubConsultant[] = data || []

  const handleOpenCreate = () => {
    setEditingSub(null)
    setShowModal(true)
  }

  const handleOpenEdit = (sub: SubConsultant) => {
    setEditingSub(sub)
    setShowModal(true)
  }

  const handleSubmit = (formData: SubConsultantData) => {
    if (editingSub) {
      updateMutation.mutate({ id: editingSub.id, data: formData })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-heading-lg text-text-primary">Sub-Consultants</h1>
          <p className="mt-1 text-ui-base text-text-secondary">
            Manage your sub-consultant partner registry.
          </p>
        </div>
        <Button onClick={handleOpenCreate}>
          <Plus className="h-4 w-4" />
          Add Sub-Consultant
        </Button>
      </div>

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-text-tertiary">Loading sub-consultants...</div>
        </div>
      ) : subs.length === 0 ? (
        /* Empty State */
        <div className="panel p-12 text-center border-dashed">
          <Users className="mx-auto h-12 w-12 text-text-tertiary" />
          <p className="mt-4 text-heading-sm text-text-primary">No sub-consultants yet</p>
          <p className="mt-2 text-text-secondary">
            Add your preferred sub-consultant partners to enable automatic matching.
          </p>
          <div className="mt-6">
            <p className="text-ui-sm text-text-tertiary mb-3">Common disciplines:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {COMMON_DISCIPLINES.slice(0, 6).map((d) => (
                <Badge key={d} variant="default">
                  {d}
                </Badge>
              ))}
            </div>
          </div>
          <div className="mt-6">
            <Button onClick={handleOpenCreate}>
              <Plus className="h-4 w-4" />
              Add Your First Sub-Consultant
            </Button>
          </div>
        </div>
      ) : (
        /* Cards Grid */
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {subs.map((sub) => (
            <div key={sub.id} className="panel p-4 relative group">
              {/* Edit/Delete buttons */}
              <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                <button
                  onClick={() => handleOpenEdit(sub)}
                  className="p-1.5 rounded hover:bg-surface-secondary text-text-tertiary hover:text-text-primary"
                  title="Edit"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setDeleteConfirm(sub.id)}
                  className="p-1.5 rounded hover:bg-red-50 text-text-tertiary hover:text-red-600"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="flex items-start justify-between mb-3 pr-16">
                <div>
                  <h3 className="text-heading-sm text-text-primary">{sub.company_name}</h3>
                  <p className="text-ui-sm text-text-tertiary">{sub.discipline}</p>
                </div>
              </div>

              <div className="flex gap-2 mb-3">
                <TierBadge tier={sub.tier} />
                <CapacityBadge capacity={sub.capacity_status} />
              </div>

              <div className="flex items-center gap-4 text-ui-sm text-text-secondary mb-3">
                {sub.win_rate_together !== undefined && (
                  <div className="flex items-center gap-1">
                    <Briefcase className="h-3.5 w-3.5 text-text-tertiary" />
                    <ScoreBadge value={Math.round(sub.win_rate_together * 100)} />
                    <span className="text-text-tertiary">win rate</span>
                  </div>
                )}
                <div>{sub.past_joint_projects} joint projects</div>
              </div>

              {sub.typical_fee_range_low && sub.typical_fee_range_high && (
                <p className="text-ui-sm text-text-secondary mb-3">
                  Fee range: ${sub.typical_fee_range_low.toLocaleString()} - $
                  {sub.typical_fee_range_high.toLocaleString()}
                </p>
              )}

              {(sub.primary_contact_name || sub.primary_contact_email) && (
                <div className="pt-3 border-t border-border text-ui-sm">
                  {sub.primary_contact_name && (
                    <p className="text-text-primary">{sub.primary_contact_name}</p>
                  )}
                  {sub.primary_contact_email && (
                    <p className="flex items-center gap-1.5 text-text-tertiary">
                      <Mail className="h-3 w-3" />
                      {sub.primary_contact_email}
                    </p>
                  )}
                  {sub.primary_contact_phone && (
                    <p className="flex items-center gap-1.5 text-text-tertiary">
                      <Phone className="h-3 w-3" />
                      {sub.primary_contact_phone}
                    </p>
                  )}
                </div>
              )}

              {sub.notes && (
                <p className="mt-3 text-ui-sm text-text-tertiary line-clamp-2">{sub.notes}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Modal */}
      {showModal && (
        <SubConsultantModal
          sub={editingSub}
          onClose={() => {
            setShowModal(false)
            setEditingSub(null)
          }}
          onSubmit={handleSubmit}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}

      {/* Delete Confirmation */}
      {deleteConfirm && (
        <DeleteConfirmModal
          companyName={subs.find((s) => s.id === deleteConfirm)?.company_name || ''}
          onConfirm={() => handleDelete(deleteConfirm)}
          onCancel={() => setDeleteConfirm(null)}
          isLoading={deleteMutation.isPending}
        />
      )}
    </div>
  )
}

function TierBadge({ tier }: { tier: string }) {
  const isTier1 = tier === 'tier_1'
  return <Badge variant={isTier1 ? 'info' : 'default'}>{isTier1 ? 'Tier 1' : 'Tier 2'}</Badge>
}

function CapacityBadge({ capacity }: { capacity: string }) {
  const variants: Record<string, 'go' | 'maybe' | 'nogo'> = {
    available: 'go',
    limited: 'maybe',
    unavailable: 'nogo',
  }
  return (
    <Badge variant={variants[capacity] || 'default'} dot>
      {capacity}
    </Badge>
  )
}

interface SubConsultantModalProps {
  sub: SubConsultant | null
  onClose: () => void
  onSubmit: (data: SubConsultantData) => void
  isLoading: boolean
}

function SubConsultantModal({ sub, onClose, onSubmit, isLoading }: SubConsultantModalProps) {
  const [formData, setFormData] = useState<SubConsultantData>({
    company_name: sub?.company_name || '',
    discipline: sub?.discipline || '',
    tier: sub?.tier || 'tier_1',
    primary_contact_name: sub?.primary_contact_name || '',
    primary_contact_email: sub?.primary_contact_email || '',
    primary_contact_phone: sub?.primary_contact_phone || '',
    past_joint_projects: sub?.past_joint_projects || 0,
    win_rate_together: sub?.win_rate_together || undefined,
    typical_fee_range_low: sub?.typical_fee_range_low || undefined,
    typical_fee_range_high: sub?.typical_fee_range_high || undefined,
    notes: sub?.notes || '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-primary rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-heading-md text-text-primary">
            {sub ? 'Edit Sub-Consultant' : 'Add Sub-Consultant'}
          </h2>
          <button onClick={onClose} className="text-text-tertiary hover:text-text-primary">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Company Info */}
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="block text-ui-sm font-medium text-text-primary mb-1">
                Company Name *
              </label>
              <input
                type="text"
                required
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                placeholder="ABC Engineering Ltd."
              />
            </div>
            <div>
              <label className="block text-ui-sm font-medium text-text-primary mb-1">
                Discipline *
              </label>
              <input
                type="text"
                required
                list="disciplines"
                value={formData.discipline}
                onChange={(e) => setFormData({ ...formData, discipline: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                placeholder="Geotechnical Engineering"
              />
              <datalist id="disciplines">
                {COMMON_DISCIPLINES.map((d) => (
                  <option key={d} value={d} />
                ))}
              </datalist>
            </div>
          </div>

          {/* Tier */}
          <div>
            <label className="block text-ui-sm font-medium text-text-primary mb-1">
              Partner Tier *
            </label>
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="tier"
                  value="tier_1"
                  checked={formData.tier === 'tier_1'}
                  onChange={() => setFormData({ ...formData, tier: 'tier_1' })}
                  className="text-accent-primary focus:ring-accent-primary"
                />
                <span className="text-text-primary">Tier 1 (Preferred)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="tier"
                  value="tier_2"
                  checked={formData.tier === 'tier_2'}
                  onChange={() => setFormData({ ...formData, tier: 'tier_2' })}
                  className="text-accent-primary focus:ring-accent-primary"
                />
                <span className="text-text-primary">Tier 2 (Backup)</span>
              </label>
            </div>
          </div>

          {/* Contact Info */}
          <div className="border-t border-border pt-4">
            <h3 className="text-ui-sm font-medium text-text-primary mb-3">Primary Contact</h3>
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">Name</label>
                <input
                  type="text"
                  value={formData.primary_contact_name || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, primary_contact_name: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="John Smith"
                />
              </div>
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">Email</label>
                <input
                  type="email"
                  value={formData.primary_contact_email || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, primary_contact_email: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="john@example.com"
                />
              </div>
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">Phone</label>
                <input
                  type="tel"
                  value={formData.primary_contact_phone || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, primary_contact_phone: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="416-555-1234"
                />
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="border-t border-border pt-4">
            <h3 className="text-ui-sm font-medium text-text-primary mb-3">Performance</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">
                  Past Joint Projects
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.past_joint_projects || 0}
                  onChange={(e) =>
                    setFormData({ ...formData, past_joint_projects: parseInt(e.target.value) || 0 })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                />
              </div>
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">
                  Win Rate Together (0-100%)
                </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={
                    formData.win_rate_together !== undefined
                      ? Math.round(formData.win_rate_together * 100)
                      : ''
                  }
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      win_rate_together: e.target.value ? parseInt(e.target.value) / 100 : undefined,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="65"
                />
              </div>
            </div>
          </div>

          {/* Fee Range */}
          <div className="border-t border-border pt-4">
            <h3 className="text-ui-sm font-medium text-text-primary mb-3">Typical Fee Range</h3>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">Low ($)</label>
                <input
                  type="number"
                  min="0"
                  value={formData.typical_fee_range_low || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      typical_fee_range_low: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="15000"
                />
              </div>
              <div>
                <label className="block text-ui-sm text-text-secondary mb-1">High ($)</label>
                <input
                  type="number"
                  min="0"
                  value={formData.typical_fee_range_high || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      typical_fee_range_high: e.target.value ? parseInt(e.target.value) : undefined,
                    })
                  }
                  className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary"
                  placeholder="50000"
                />
              </div>
            </div>
          </div>

          {/* Notes */}
          <div className="border-t border-border pt-4">
            <label className="block text-ui-sm font-medium text-text-primary mb-1">Notes</label>
            <textarea
              value={formData.notes || ''}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 border border-border rounded-md bg-surface-primary text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary resize-none"
              placeholder="Preferred for municipal work, very responsive..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Saving...' : sub ? 'Update' : 'Add Sub-Consultant'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface DeleteConfirmModalProps {
  companyName: string
  onConfirm: () => void
  onCancel: () => void
  isLoading: boolean
}

function DeleteConfirmModal({
  companyName,
  onConfirm,
  onCancel,
  isLoading,
}: DeleteConfirmModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-primary rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-heading-md text-text-primary mb-2">Delete Sub-Consultant?</h2>
        <p className="text-text-secondary mb-6">
          Are you sure you want to delete <strong>{companyName}</strong>? This action cannot be
          undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button
            variant="secondary"
            onClick={onConfirm}
            disabled={isLoading}
            className="!bg-red-600 !text-white hover:!bg-red-700"
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </Button>
        </div>
      </div>
    </div>
  )
}
