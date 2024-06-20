/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/

import _ from "lodash";
import i18n from "i18n";

export const selectTeamUsageStats = (state) => {
  if (!_.isEmpty(state.team?.teamInfo?.data)) {
    const { data } = state.team?.teamInfo;

    const getPercentage = (credits, creditsUsed) => {
      return _.floor(_.divide(creditsUsed || 0, credits || 1) * 100, 2);
    };

    const getMemoryGb = (credit) => {
      if (credit) {
        return _.floor(_.divide(credit, 1000), 3);
      }
      return 0;
    };

    const getTimeHours = (credit) => {
      if (credit) {
        return _.floor(_.divide(credit, 3600), 2);
      }
      return 0;
    };

    return [
      {
        name: i18n.t(`team:cpu_usage_subscription`),
        credits: getTimeHours(data?.cpu_usage_subscription?.credits, 3600),
        creditsUsage: getTimeHours(data?.cpu_usage_subscription?.credits_used),
        persantage: getPercentage(
          data?.cpu_usage_subscription?.credits,
          data?.cpu_usage_subscription?.credits_used,
        ),
        unit: "Hrs",
        isPurchased: false,
        isPrimary: true,
        isShowAtTools: false,
      },
      {
        name: i18n.t(`team:storage_usage_subscription`),
        credits: getMemoryGb(data?.storage_usage_subscription?.credits),
        creditsUsage: getMemoryGb(data?.storage_usage_subscription?.credits_used),
        persantage: getPercentage(
          data?.storage_usage_subscription?.credits,
          data?.storage_usage_subscription?.credits_used,
        ),
        unit: "Gb",
        isPurchased: false,
        isPrimary: true,
        isShowAtTools: true,
      },
      {
        name: i18n.t(`team:cpu_usage_purchased`),
        credits: getTimeHours(data?.cpu_usage_purchased?.credits, 3600),
        creditsUsage: getTimeHours(data?.cpu_usage_purchased?.credits_used),
        persantage: getPercentage(
          data?.cpu_usage_purchased?.credits,
          data?.cpu_usage_purchased?.credits_used,
        ),
        unit: "Hrs",
        isPurchased: true,
        isPrimary: true,
        isShowAtTools: false,
      },
      {
        name: i18n.t(`team:storage_usage_purchased`),
        credits: getTimeHours(data?.storage_usage_purchased?.credits, 3600),
        creditsUsage: getTimeHours(data?.storage_usage_purchased?.credits_used),
        persantage: getPercentage(
          data?.storage_usage_purchased?.credits,
          data?.storage_usage_purchased?.credits_used,
        ),
        unit: "Gb",
        isPurchased: true,
        isPrimary: true,
        isShowAtTools: false,
      },
    ];
  }
  return [];
};

export const selectIsDemoTeam = (state) => {
  return state.auth?.teamInfo?.team === "FreeTrialDataTeam" || false;
};

export default selectTeamUsageStats;
