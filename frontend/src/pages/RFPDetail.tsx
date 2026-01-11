import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  FileText,
  Calendar,
  Building2,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Loader2,
  Phone,
  Mail,
  Briefcase,
  DollarSign,
  TrendingUp,
  MessageCircleQuestion,
  Hash,
  CalendarClock,
  Target,
} from 'lucide-react'
import { rfpApi, subConsultantsApi, budgetApi } from '../api/client'
import { Button, StatusBadge, Badge } from '../components/ui'

interface ExtractionField {
  field_name: string
  value: string
  source_page: number | null
  source_text: string | null
  confidence: number
  verified: boolean
}

interface Contradiction {
  id: string
  type: 'numerical' | 'timeline' | 'scope'
  description: string
  statement_a: string
  statement_a_page: number | null
  statement_b: string
  statement_b_page: number | null
  clarifying_question: string
  is_helpful: boolean | null
  feedback_at: string | null
}

interface RFPDetail {
  id: string
  status: string
  source: string
  filename: string
  created_at: string
  page_count: number
  has_raw_text: boolean
  fields: {
    client_name: string | null
    rfp_number: string | null
    opportunity_title: string | null
    scope_summary: string | null
    published_date: string | null
    question_deadline: string | null
    submission_deadline: string | null
    contract_duration: string | null
    required_internal_disciplines: string[] | null
    required_external_disciplines: string[] | null
    evaluation_criteria: any
    reference_requirements: any
    insurance_requirements: any
    risk_flags: string[] | null
  }
  extractions: ExtractionField[]
  contradictions: Contradiction[]
  decision_notes: string | null
  quick_scan_recommendation: string | null
}

interface SubMatch {
  id: string
  company_name: string
  contact_name: string
  contact_email: string
  contact_phone?: string
  win_rate: number
  past_projects?: number
  capacity: string
}

interface MatchResult {
  [discipline: string]: {
    tier_1: SubMatch[]
    tier_2: SubMatch[]
  }
}

interface BudgetMatch {
  budget_item_id: string
  project_name: string
  total_budget: number | null
  description: string | null
  confidence: number
  match_reason: string
  source_page: number | null
}

function FieldCard({
  label,
  value,
  extraction,
  icon: Icon,
}: {
  label: string
  value: string | null | undefined
  extraction?: ExtractionField
  icon?: any
}) {
  const [showSource, setShowSource] = useState(false)

  if (!value) return null

  return (
    <div className="panel p-4 space-y-2">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2 text-text-secondary text-ui-sm">
          {Icon && <Icon className="h-4 w-4" />}
          {label}
        </div>
        {extraction && extraction.source_page && (
          <button
            onClick={() => setShowSource(!showSource)}
            className="text-ui-xs text-accent-primary hover:text-accent-primary-hover flex items-center gap-1"
          >
            <FileText className="h-3 w-3" />
            Page {extraction.source_page}
          </button>
        )}
      </div>
      <p className="text-text-primary">{value}</p>
      {showSource && extraction?.source_text && (
        <div className="mt-2 p-2 bg-bg-tertiary rounded text-ui-sm text-text-secondary italic border-l-2 border-accent-primary">
          "{extraction.source_text}"
        </div>
      )}
    </div>
  )
}

function SubConsultantCard({ sub, tier }: { sub: SubMatch; tier: 'tier_1' | 'tier_2' }) {
  return (
    <div className="panel p-3 space-y-2">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-text-primary font-medium">{sub.company_name}</p>
          <p className="text-ui-sm text-text-secondary">{sub.contact_name}</p>
        </div>
        <div className="flex gap-2">
          <Badge variant={tier === 'tier_1' ? 'info' : 'default'}>
            {tier === 'tier_1' ? 'Tier 1' : 'Tier 2'}
          </Badge>
          <Badge variant={sub.capacity === 'available' ? 'go' : sub.capacity === 'limited' ? 'maybe' : 'nogo'} dot>
            {sub.capacity}
          </Badge>
        </div>
      </div>
      <div className="flex items-center gap-4 text-ui-sm text-text-tertiary">
        {sub.win_rate && (
          <span className="flex items-center gap-1">
            <Briefcase className="h-3 w-3" />
            {Math.round(sub.win_rate * 100)}% win rate
          </span>
        )}
        {sub.past_projects && (
          <span>{sub.past_projects} projects</span>
        )}
      </div>
      <div className="flex gap-3 text-ui-sm">
        {sub.contact_email && (
          <a href={`mailto:${sub.contact_email}`} className="flex items-center gap-1 text-accent-primary hover:underline">
            <Mail className="h-3 w-3" />
            Email
          </a>
        )}
        {sub.contact_phone && (
          <a href={`tel:${sub.contact_phone}`} className="flex items-center gap-1 text-accent-primary hover:underline">
            <Phone className="h-3 w-3" />
            {sub.contact_phone}
          </a>
        )}
      </div>
    </div>
  )
}

function BudgetMatchCard({ match }: { match: BudgetMatch }) {
  return (
    <div className="panel p-4 border-green-500/20 bg-green-500/5">
      <div className="flex items-start justify-between mb-2">
        <div>
          <p className="text-text-primary font-medium">{match.project_name}</p>
          {match.total_budget && (
            <p className="text-green-400 font-medium flex items-center gap-1 mt-1">
              <DollarSign className="h-4 w-4" />
              {match.total_budget.toLocaleString('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 })}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="go">
            {Math.round(match.confidence * 100)}% match
          </Badge>
          {match.source_page && (
            <span className="text-ui-xs text-text-tertiary">p.{match.source_page}</span>
          )}
        </div>
      </div>
      {match.description && (
        <p className="text-ui-sm text-text-secondary mt-2">{match.description}</p>
      )}
      <p className="text-ui-xs text-text-tertiary mt-2 italic">{match.match_reason}</p>
    </div>
  )
}

function ContradictionCard({
  contradiction,
  onFeedback,
  isSubmitting,
}: {
  contradiction: Contradiction
  onFeedback: (id: string, isHelpful: boolean) => void
  isSubmitting: boolean
}) {
  const typeIcons = {
    numerical: Hash,
    timeline: CalendarClock,
    scope: Target,
  }
  const typeColors = {
    numerical: 'text-blue-400 bg-blue-500/10',
    timeline: 'text-purple-400 bg-purple-500/10',
    scope: 'text-orange-400 bg-orange-500/10',
  }

  const TypeIcon = typeIcons[contradiction.type]

  return (
    <div className="panel p-4 border-amber-500/30 bg-amber-500/5 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded text-ui-xs font-medium flex items-center gap-1 ${typeColors[contradiction.type]}`}>
            <TypeIcon className="h-3 w-3" />
            {contradiction.type.charAt(0).toUpperCase() + contradiction.type.slice(1)}
          </span>
        </div>
        {/* Feedback buttons */}
        <div className="flex items-center gap-2">
          {contradiction.is_helpful === null ? (
            <>
              <button
                onClick={() => onFeedback(contradiction.id, true)}
                disabled={isSubmitting}
                className="p-1.5 rounded hover:bg-green-500/20 text-text-tertiary hover:text-green-400 transition-colors disabled:opacity-50"
                title="Helpful"
              >
                <ThumbsUp className="h-4 w-4" />
              </button>
              <button
                onClick={() => onFeedback(contradiction.id, false)}
                disabled={isSubmitting}
                className="p-1.5 rounded hover:bg-red-500/20 text-text-tertiary hover:text-red-400 transition-colors disabled:opacity-50"
                title="Not helpful"
              >
                <ThumbsDown className="h-4 w-4" />
              </button>
            </>
          ) : (
            <span className={`text-ui-xs ${contradiction.is_helpful ? 'text-green-400' : 'text-red-400'}`}>
              {contradiction.is_helpful ? 'Marked helpful' : 'Marked not helpful'}
            </span>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-text-primary font-medium">{contradiction.description}</p>

      {/* Conflicting statements */}
      <div className="space-y-2">
        <div className="p-2 bg-bg-tertiary rounded border-l-2 border-red-500/50">
          <div className="flex items-center justify-between mb-1">
            <span className="text-ui-xs text-text-tertiary">Statement A</span>
            {contradiction.statement_a_page && (
              <span className="text-ui-xs text-accent-primary">Page {contradiction.statement_a_page}</span>
            )}
          </div>
          <p className="text-ui-sm text-text-secondary italic">"{contradiction.statement_a}"</p>
        </div>
        <div className="p-2 bg-bg-tertiary rounded border-l-2 border-red-500/50">
          <div className="flex items-center justify-between mb-1">
            <span className="text-ui-xs text-text-tertiary">Statement B</span>
            {contradiction.statement_b_page && (
              <span className="text-ui-xs text-accent-primary">Page {contradiction.statement_b_page}</span>
            )}
          </div>
          <p className="text-ui-sm text-text-secondary italic">"{contradiction.statement_b}"</p>
        </div>
      </div>

      {/* Clarifying question */}
      <div className="p-3 bg-accent-primary/10 rounded border border-accent-primary/30">
        <div className="flex items-center gap-2 text-accent-primary text-ui-sm mb-1">
          <MessageCircleQuestion className="h-4 w-4" />
          Suggested Clarifying Question
        </div>
        <p className="text-text-primary text-ui-sm">{contradiction.clarifying_question}</p>
      </div>
    </div>
  )
}

export default function RFPDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isExtracting, setIsExtracting] = useState(false)
  const [subMatches, setSubMatches] = useState<MatchResult | null>(null)
  const [budgetMatches, setBudgetMatches] = useState<BudgetMatch[]>([])

  const { data: rfp, isLoading, error } = useQuery<RFPDetail>({
    queryKey: ['rfp', id],
    queryFn: () => rfpApi.getDetail(id!),
    enabled: !!id,
  })

  // Fetch sub-consultant matches
  useEffect(() => {
    if (rfp?.fields?.required_external_disciplines?.length) {
      subConsultantsApi.match(rfp.fields.required_external_disciplines)
        .then(setSubMatches)
        .catch(console.error)
    }
  }, [rfp?.fields?.required_external_disciplines])

  // Fetch budget matches
  useEffect(() => {
    if (rfp?.id && rfp?.fields?.scope_summary) {
      budgetApi.matchToRfp(rfp.id)
        .then((data) => setBudgetMatches(data.matches || []))
        .catch(console.error)
    }
  }, [rfp?.id, rfp?.fields?.scope_summary])

  const extractMutation = useMutation({
    mutationFn: () => rfpApi.extract(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfp', id] })
      setIsExtracting(false)
    },
    onError: () => {
      setIsExtracting(false)
    },
  })

  const decideMutation = useMutation({
    mutationFn: ({ decision, notes }: { decision: 'go' | 'no_go'; notes?: string }) =>
      rfpApi.decide(id!, decision, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfp', id] })
    },
  })

  const feedbackMutation = useMutation({
    mutationFn: ({ contradictionId, isHelpful }: { contradictionId: string; isHelpful: boolean }) =>
      rfpApi.submitContradictionFeedback(id!, contradictionId, isHelpful),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rfp', id] })
    },
  })

  const handleContradictionFeedback = (contradictionId: string, isHelpful: boolean) => {
    feedbackMutation.mutate({ contradictionId, isHelpful })
  }

  const handleExtract = () => {
    setIsExtracting(true)
    extractMutation.mutate()
  }

  const getExtraction = (fieldName: string) => {
    return rfp?.extractions.find((e) => e.field_name === fieldName)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-text-tertiary" />
      </div>
    )
  }

  if (error || !rfp) {
    return (
      <div className="panel p-8 text-center">
        <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-text-primary">Failed to load RFP details</p>
        <Button onClick={() => navigate('/rfps')} className="mt-4">
          Back to RFPs
        </Button>
      </div>
    )
  }

  const hasExtractions = rfp.extractions.length > 0
  const needsExtraction = rfp.has_raw_text && !hasExtractions

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/rfps')}
            className="p-2 hover:bg-bg-secondary rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-text-secondary" />
          </button>
          <div>
            <h1 className="text-heading-lg text-text-primary">
              {rfp.fields.client_name || rfp.filename || 'Untitled RFP'}
            </h1>
            <div className="flex items-center gap-3 mt-1">
              <StatusBadge status={rfp.status as any} />
              {rfp.page_count && (
                <span className="text-ui-sm text-text-tertiary">
                  {rfp.page_count} pages
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {needsExtraction && (
            <Button onClick={handleExtract} disabled={isExtracting}>
              {isExtracting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Extracting...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Extract with Claude
                </>
              )}
            </Button>
          )}

          {hasExtractions && rfp.status !== 'go' && rfp.status !== 'no_go' && (
            <>
              <Button
                variant="secondary"
                onClick={() => decideMutation.mutate({ decision: 'no_go' })}
              >
                <ThumbsDown className="h-4 w-4" />
                NO-GO
              </Button>
              <Button onClick={() => decideMutation.mutate({ decision: 'go' })}>
                <ThumbsUp className="h-4 w-4" />
                GO
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Extraction CTA */}
      {needsExtraction && (
        <div className="panel p-6 border-dashed border-accent-primary/30 bg-accent-primary/5">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-accent-primary/10 rounded-lg">
              <Sparkles className="h-6 w-6 text-accent-primary" />
            </div>
            <div>
              <h3 className="text-heading-sm text-text-primary">Ready for AI Extraction</h3>
              <p className="text-text-secondary mt-1">
                Claude will analyze the {rfp.page_count}-page document and extract key fields.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Budget Match Banner */}
      {budgetMatches.length > 0 && (
        <div className="panel p-4 border-green-500/30 bg-green-500/5">
          <div className="flex items-center gap-2 text-green-400 mb-3">
            <TrendingUp className="h-5 w-5" />
            <span className="font-medium">Budget Match Found</span>
          </div>
          <div className="space-y-3">
            {budgetMatches.slice(0, 2).map((match, i) => (
              <BudgetMatchCard key={i} match={match} />
            ))}
          </div>
        </div>
      )}

      {/* Contradictions Section */}
      {rfp.contradictions && rfp.contradictions.length > 0 && (
        <div className="panel p-4 border-amber-500/30 bg-amber-500/5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-medium">
                {rfp.contradictions.length} Contradiction{rfp.contradictions.length !== 1 ? 's' : ''} Found
              </span>
            </div>
            <span className="text-ui-xs text-text-tertiary">
              Review and clarify with client before submitting
            </span>
          </div>
          <div className="space-y-4">
            {rfp.contradictions.map((contradiction) => (
              <ContradictionCard
                key={contradiction.id}
                contradiction={contradiction}
                onFeedback={handleContradictionFeedback}
                isSubmitting={feedbackMutation.isPending}
              />
            ))}
          </div>
        </div>
      )}

      {/* Extracted Fields */}
      {hasExtractions && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-4">
            <h2 className="text-heading-sm text-text-primary flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Key Information
            </h2>

            <FieldCard
              label="Client"
              value={rfp.fields.client_name}
              extraction={getExtraction('client_name')}
              icon={Building2}
            />

            <FieldCard
              label="Scope Summary"
              value={rfp.fields.scope_summary}
              extraction={getExtraction('scope_summary')}
              icon={FileText}
            />

            {(rfp.fields.submission_deadline || rfp.fields.question_deadline) && (
              <div className="panel p-4 space-y-3">
                <div className="flex items-center gap-2 text-text-secondary text-ui-sm">
                  <Calendar className="h-4 w-4" />
                  Key Dates
                </div>
                {rfp.fields.submission_deadline && (
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Submission Deadline</span>
                    <span className="text-text-primary font-medium">
                      {new Date(rfp.fields.submission_deadline).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {rfp.fields.question_deadline && (
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Questions Due</span>
                    <span className="text-text-primary">
                      {new Date(rfp.fields.question_deadline).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Internal Disciplines */}
            {rfp.fields.required_internal_disciplines && rfp.fields.required_internal_disciplines.length > 0 && (
              <div className="panel p-4">
                <div className="flex items-center gap-2 text-text-secondary text-ui-sm mb-3">
                  <Users className="h-4 w-4" />
                  Internal Disciplines
                </div>
                <div className="flex flex-wrap gap-2">
                  {rfp.fields.required_internal_disciplines.map((d, i) => (
                    <span key={i} className="px-2 py-1 rounded text-ui-sm bg-blue-500/10 text-blue-400">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-heading-sm text-text-primary flex items-center gap-2">
              <Users className="h-5 w-5" />
              Sub-Consultants Needed
            </h2>

            {/* Sub-Consultant Matches */}
            {subMatches && Object.keys(subMatches).length > 0 ? (
              Object.entries(subMatches).map(([discipline, matches]) => (
                <div key={discipline} className="space-y-2">
                  <h3 className="text-ui-sm text-text-secondary font-medium">
                    <span className="px-2 py-0.5 rounded bg-orange-500/10 text-orange-400">
                      {discipline}
                    </span>
                  </h3>
                  {matches.tier_1.length > 0 ? (
                    matches.tier_1.map((sub) => (
                      <SubConsultantCard key={sub.id} sub={sub} tier="tier_1" />
                    ))
                  ) : matches.tier_2.length > 0 ? (
                    matches.tier_2.map((sub) => (
                      <SubConsultantCard key={sub.id} sub={sub} tier="tier_2" />
                    ))
                  ) : (
                    <p className="text-ui-sm text-text-tertiary italic">No matches</p>
                  )}
                </div>
              ))
            ) : rfp.fields.required_external_disciplines?.length ? (
              <div className="panel p-4 border-dashed">
                <p className="text-text-secondary text-ui-sm">
                  No sub-consultants registered for these disciplines.
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {rfp.fields.required_external_disciplines.map((d, i) => (
                    <span key={i} className="px-2 py-1 rounded text-ui-sm bg-orange-500/10 text-orange-400">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {/* Risk Flags */}
            {rfp.fields.risk_flags && rfp.fields.risk_flags.length > 0 && (
              <div className="panel p-4 border-yellow-500/30 bg-yellow-500/5">
                <div className="flex items-center gap-2 text-yellow-500 text-ui-sm mb-3">
                  <AlertTriangle className="h-4 w-4" />
                  Risk Flags
                </div>
                <ul className="space-y-2">
                  {rfp.fields.risk_flags.map((flag, i) => (
                    <li key={i} className="text-text-secondary text-ui-sm">
                      • {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Extractions Table */}
      {hasExtractions && (
        <div className="panel p-4">
          <h3 className="text-heading-sm text-text-primary mb-4">
            All Extractions ({rfp.extractions.length} fields)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-primary">
                  <th className="text-left py-2 text-ui-sm text-text-secondary font-medium">Field</th>
                  <th className="text-left py-2 text-ui-sm text-text-secondary font-medium">Value</th>
                  <th className="text-center py-2 text-ui-sm text-text-secondary font-medium">Page</th>
                  <th className="text-center py-2 text-ui-sm text-text-secondary font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {rfp.extractions.map((e, i) => (
                  <tr key={i} className="border-b border-border-secondary">
                    <td className="py-2 text-text-secondary">{e.field_name}</td>
                    <td className="py-2 text-text-primary max-w-md truncate">
                      {e.value.length > 80 ? e.value.substring(0, 80) + '...' : e.value}
                    </td>
                    <td className="py-2 text-center">
                      {e.source_page && (
                        <span className="text-accent-primary text-ui-sm">p.{e.source_page}</span>
                      )}
                    </td>
                    <td className="py-2 text-center">
                      {e.verified ? (
                        <CheckCircle className="h-4 w-4 text-green-500 mx-auto" />
                      ) : (
                        <Clock className="h-4 w-4 text-yellow-500 mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
