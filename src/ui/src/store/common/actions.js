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

import {
  STORE_ACTIVE_VIEW,
  STORE_HAS_UNSAVED_CHANGES,
  STORE_NAV_BAR_STATE,
  STORE_IS_MAIN_SCREEN_LOADING,
  SET_IS_SHOW_BANNER_OFFER,
  SET_IS_SHOW_BANNER_MAINTENANCE,
} from "./actionTypes";

export const setActiveView = (viewId) => {
  return {
    type: STORE_ACTIVE_VIEW,
    activeView: viewId,
  };
};

export const setHasUnsavedChanges = (value) => {
  return {
    type: STORE_HAS_UNSAVED_CHANGES,
    hasUnsavedChanges: value,
  };
};

export const setNavBarState = (value) => {
  return {
    type: STORE_NAV_BAR_STATE,
    isOpen: value,
  };
};

export const setIsMainScreenLoading = (value) => {
  return {
    type: STORE_IS_MAIN_SCREEN_LOADING,
    payload: value,
  };
};

export const setIsShowBannerOffer = (value) => {
  return {
    type: SET_IS_SHOW_BANNER_OFFER,
    payload: value,
  };
};

export const setIsShowBannerMaintenance = (value) => {
  return {
    type: SET_IS_SHOW_BANNER_MAINTENANCE,
    payload: value,
  };
};

export const setShowBannersAfterLogin = () => async (dispatch) => {
  /* offers
  if (false && ["STARTER", "UNSUBSCRIBED", "FREE", "DEVELOPER"].includes(teamInfo?.subscription)) {
    const isOfferActive = new Date() <= new Date("2021-09-30");
    if (isOfferActive) {
      dispatch(setIsShowBannerOffer(isOfferActive));
    }
  }
  */
  if (new Date() <= new Date("2023-05-15T21:00:00-07:00")) {
    dispatch(setIsShowBannerMaintenance(true));
  }
};

export const setShowBannersBeforeLogin = (teamInfo) => async (dispatch) => {
  if (["STARTER", "UNSUBSCRIBED", "FREE", "DEVELOPER"].includes(teamInfo?.subscription)) {
    const isOfferActive = new Date() <= new Date("2021-09-30");
    dispatch(setIsShowBannerOffer(isOfferActive));
  }
};
