export interface StatItem {
  id: number
  label: string
  value: number
  icon: string
  iconColor: 'blue' | 'orange' | 'red' | 'green'
  change?: string
  subtitle?: string
}

export interface TenantTrackerItem {
  id: number
  name: string
  initials: string
  phone: string
  room: string
  floor: string
  status: {
    type: 'success' | 'warning' | 'danger'
    label: string
  }
  dueDate: string
  action: string
  color: 'purple' | 'blue' | 'red' | 'green'
}
