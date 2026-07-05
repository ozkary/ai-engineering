/**
 * @file  src/services/salesDashboard/models.ts
 * @description  business domain models for the sales dashboard service
 *
 * @author ogarcia (ozkary)
 *
 */

import type { SalesData } from "../../apis/salesDashboard/model";

export interface SalesDashboardData {
  regions: (SalesData & { formattedRevenue: string })[];
  total: number;
}
