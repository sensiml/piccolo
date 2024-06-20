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

import { connect } from "react-redux";
import { loadTeamInfo } from "store/team/actions";
import { selectTeamUsageStats } from "store/team/selectors";

import TheAccountSubscription from "./TheAccountSubscription";

const mapStateToProps = (state) => {
  return {
    userId: state?.auth?.userId,
    teamName: state?.auth?.teamInfo?.team || "",
    subscription: state?.auth?.teamInfo?.subscription || "",
    teamUsageStats: selectTeamUsageStats(state),
    teamUsageStatsIsLoading: state?.team?.teamInfo?.isFetching || false,
  };
};

const mapDispatchToProps = { loadTeamInfo };

export default connect(mapStateToProps, mapDispatchToProps)(TheAccountSubscription);
