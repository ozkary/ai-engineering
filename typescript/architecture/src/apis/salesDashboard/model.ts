/**
 * @file  src/apis/salesDashboard/models.ts
 * @description  data definitions for the sales dashboard api layer
 *
 * @author ogarcia (ozkary)
 *
 */
export interface SalesData {
  id: number;
  region: string;
  revenue: number;
  growth: number;
}

/**
 * @file  src/apis/salesDashboard/mock.ts
 * @description  mock data for the sales dashboard api
 *
 * @author ogarcia (ozkary)
 *
 */
export const MOCK_SALES_DATA: SalesData[] = [
  { id: 1, region: 'North America', revenue: 1250000, growth: 15 },
  { id: 2, region: 'Europe', revenue: 980000, growth: 8 },
  { id: 3, region: 'Asia Pacific', revenue: 1450000, growth: 22 },
];