import { useQuery } from '@tanstack/react-query'

interface DataRange {
  start_date: string
  end_date: string
  total_days: number
}

export function useDataRange() {
  return useQuery<DataRange>({
    queryKey: ['data-range'],
    queryFn: async () => {
      const response = await fetch('http://localhost:8000/api/runs/data-range')
      if (!response.ok) {
        throw new Error('Failed to fetch data range')
      }
      return response.json()
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1
  })
}
