import { useQuery } from '@tanstack/react-query'
import { Users, Plus } from 'lucide-react'
import { subConsultantsApi } from '../api/client'

export default function SubConsultants() {
  const { data, isLoading } = useQuery({
    queryKey: ['subconsultants'],
    queryFn: () => subConsultantsApi.list(),
  })

  const subs = data || []

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sub-Consultants</h1>
          <p className="mt-1 text-gray-600">
            Manage your sub-consultant partner registry.
          </p>
        </div>
        <button
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          onClick={() => alert('Add sub-consultant form coming soon!')}
        >
          <Plus className="h-4 w-4" />
          Add Sub-Consultant
        </button>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Loading sub-consultants...</div>
      ) : subs.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-4 text-lg font-medium text-gray-900">
            No sub-consultants yet
          </p>
          <p className="mt-2 text-gray-500">
            Add your preferred sub-consultant partners to enable automatic matching.
          </p>
          <div className="mt-4">
            <p className="text-sm text-gray-400">Typical disciplines:</p>
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              {[
                'Geotechnical',
                'Topographic Survey',
                'Archaeological',
                'Traffic Engineering',
                'Environmental',
                'Structural',
              ].map((d) => (
                <span
                  key={d}
                  className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-600"
                >
                  {d}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {subs.map((sub: any) => (
            <div
              key={sub.id}
              className="rounded-lg border border-gray-200 bg-white p-6"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-gray-900">
                      {sub.company_name}
                    </h3>
                    <TierBadge tier={sub.tier} />
                    <CapacityBadge capacity={sub.capacity_status} />
                  </div>
                  <p className="mt-1 text-sm text-gray-500">{sub.discipline}</p>
                </div>
                <div className="text-right">
                  {sub.win_rate_together && (
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">
                        {Math.round(sub.win_rate_together * 100)}%
                      </span>{' '}
                      win rate
                    </p>
                  )}
                  <p className="text-xs text-gray-500">
                    {sub.past_joint_projects} joint projects
                  </p>
                </div>
              </div>

              {(sub.primary_contact_name || sub.primary_contact_email) && (
                <div className="mt-4 border-t border-gray-100 pt-4">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Contact:</span>{' '}
                    {sub.primary_contact_name}
                    {sub.primary_contact_email && (
                      <span className="text-gray-400">
                        {' '}
                        &bull; {sub.primary_contact_email}
                      </span>
                    )}
                    {sub.primary_contact_phone && (
                      <span className="text-gray-400">
                        {' '}
                        &bull; {sub.primary_contact_phone}
                      </span>
                    )}
                  </p>
                </div>
              )}

              {sub.notes && (
                <p className="mt-2 text-sm text-gray-500">{sub.notes}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TierBadge({ tier }: { tier: string }) {
  const isTier1 = tier === 'tier_1'
  return (
    <span
      className={`rounded px-2 py-0.5 text-xs font-medium ${
        isTier1
          ? 'bg-blue-100 text-blue-700'
          : 'bg-gray-100 text-gray-600'
      }`}
    >
      {isTier1 ? 'Tier 1' : 'Tier 2'}
    </span>
  )
}

function CapacityBadge({ capacity }: { capacity: string }) {
  const colors: Record<string, string> = {
    available: 'bg-green-100 text-green-700',
    limited: 'bg-yellow-100 text-yellow-700',
    unavailable: 'bg-red-100 text-red-700',
  }

  return (
    <span
      className={`rounded px-2 py-0.5 text-xs font-medium ${
        colors[capacity] || colors.available
      }`}
    >
      {capacity}
    </span>
  )
}
