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

import { combineReducers } from "redux";
import {
  STORE_ACTIVE_VIEW,
  STORE_HAS_UNSAVED_CHANGES,
  STORE_NAV_BAR_STATE,
  STORE_IS_MAIN_SCREEN_LOADING,
  SET_IS_SHOW_BANNER_OFFER,
  SET_IS_SHOW_BANNER_MAINTENANCE,
} from "./actionTypes";

const initialActiveViewState = {
  activeView: 0,
  projectViewType: "table",
  hasUnsavedChanges: false,
  navBarIsOpen: true,
};

const values = (state = initialActiveViewState, action) => {
  switch (action.type) {
    case STORE_ACTIVE_VIEW:
      return { ...state, activeView: action.activeView };
    case STORE_HAS_UNSAVED_CHANGES:
      return { ...state, hasUnsavedChanges: action.hasUnsavedChanges };
    case STORE_NAV_BAR_STATE:
      return { ...state, navBarIsOpen: action.isOpen };
    default:
      return state;
  }
};

const initialLoadersState = {
  isMainScreenLoading: false,
};

const loaders = (state = initialLoadersState, action) => {
  switch (action.type) {
    case STORE_IS_MAIN_SCREEN_LOADING:
      return { ...state, isMainScreenLoading: action.payload };
    default:
      return state;
  }
};

const banners = (state = { isShowBannerOffer: false, isShowBannerMaintenance: false }, action) => {
  switch (action.type) {
    case SET_IS_SHOW_BANNER_OFFER:
      return { ...state, isShowBannerOffer: action.payload };
    case SET_IS_SHOW_BANNER_MAINTENANCE:
      return { ...state, isShowBannerMaintenance: action.payload };
    default:
      return state;
  }
};

export default combineReducers({
  values,
  loaders,
  banners,
});
