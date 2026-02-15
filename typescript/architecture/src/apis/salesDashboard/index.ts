
/**
 * @file  src/apis/salesDashboard/index.ts
 * @description  api client for fetching sales dashboard data
 *
 * @author ogarcia (ozkary)
 *
 */

import { MOCK_SALES_DATA, type SalesData } from "./model";

export const salesApi = {
  get: async (): Promise<SalesData[]> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_SALES_DATA);
      }, 800);
    });
  }
};