/**
 * @file  src/services/salesDashboard/index.ts
 * @description  business logic and data transformation for sales dashboard
 *
 * @author ogarcia (ozkary)
 *
 */

import { salesApi } from "../../apis/salesDashboard";
import type { SalesDashboardData } from "./model";

export const salesService = {
  getFormattedSales: async (): Promise<SalesDashboardData> => {
    try {
      const rawData = await salesApi.get();
      const total = rawData.reduce((acc, curr) => acc + curr.revenue, 0);
      const regions = rawData.map((item) => ({
        ...item,
        formattedRevenue: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(item.revenue)
      }));
      return { regions, total };
    } catch (error) {
      console.error("Service Error:", error);
      throw error;
    }
  }
};