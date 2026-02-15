/**
 * @file  src/containers/SalesDashboard/index.ts
 * @description  controller to manage state and logic for the sales dashboard view
 *
 * @author ogarcia (ozkary)
 *
 */

import { useEffect, useState } from "react";
import type { SalesDashboardData } from "../../services/salesDashboard/model";
import { salesService } from "../../services/salesDashboard";

const salesDashboardController = () => {
  const [data, setData] = useState<SalesDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await salesService.getFormattedSales();
      setData(result);
    } catch (err) {
      setError("Failed to load sales data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  return { data, isLoading, error, refresh: loadData };
};

export default salesDashboardController;