import httpClient from '../../../shared/utils/api/httpClient'

export interface PaymentCreate {
  kost_id: string
  tenant_id: string
  amount: number
  transaction_date: string
}

export interface ExpenseCreate {
  kost_id?: string
  region_id?: string
  category: string
  amount: number
  transaction_date: string
  description?: string
}

export interface TransactionResponse {
  id: string
  kost_id: string
  tenant_id: string | null
  type: 'income' | 'expense'
  category: string | null
  amount: number
  transaction_date: string
  description: string | null
  region_id: string | null
  created_at: string
}

export const transactionService = {
  async createPayment(data: PaymentCreate): Promise<TransactionResponse> {
    const response = await httpClient.post('/transactions/payments', data)
    return response.data
  },

  async createExpense(data: ExpenseCreate): Promise<TransactionResponse> {
    const response = await httpClient.post('/transactions/expenses', data)
    return response.data
  },
}

export default transactionService
