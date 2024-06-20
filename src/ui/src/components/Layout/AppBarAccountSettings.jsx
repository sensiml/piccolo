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

/* eslint-disable no-shadow */
import React, { useState, useEffect } from "react";

import { useHistory } from "react-router-dom";
import { connect } from "react-redux";
import { RESPONSIVE } from "consts";
import { ROUTES } from "routers";

import { useMediaQuery } from "@mui/material";

import { logOut } from "store/auth/actions";
import { getIsFreeAccount } from "store/auth/selectors";
import { setNavBarState } from "store/common/actions";

import HeaderAppBar from "components/Layout/HeaderAppBar";
import useStyles from "components/Layout/Header.style";
import HeaderMenu from "components/Layout/HeaderMenu";

import { useWindowResize } from "hooks";

const mapStateToProps = (state) => {
  return {
    userId: state?.auth?.userId,
    isFreeAccount: getIsFreeAccount(state),
  };
};

const mapDispatchToProps = {
  logOut,
  setNavBarState,
};

const Header = ({ userId, isFreeAccount, logOut, setNavBarState }) => {
  const classes = useStyles();
  const routersHistory = useHistory();
  const smallScreenSize = useMediaQuery("(min-width:800px)");

  const [open, setOpen] = useState(smallScreenSize);
  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const isMenuOpen = Boolean(anchorEl);

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  useEffect(() => {
    setOpen(smallScreenSize);
    setNavBarState(smallScreenSize);
  }, [setNavBarState, smallScreenSize]);

  const handleDrawerOpen = () => {
    setOpen(true);
    setNavBarState(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
    setNavBarState(false);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMenuLogOut = () => {
    logOut();
  };

  const handleOpenHome = () => {
    routersHistory.push({
      pathname: ROUTES.MAIN.HOME.path,
      state: {
        isConfirmed: true,
      },
    });
  };

  return (
    <div className={classes.root}>
      <HeaderAppBar
        isOpen={open}
        isShortBtnText={isShortBtnText}
        userId={userId}
        onDrawerClose={handleDrawerClose}
        onDrawerOpen={handleDrawerOpen}
        onOpenMenu={handleProfileMenuOpen}
        headerTitle={"Account Settings"}
      />
      <HeaderMenu
        isOpen={isMenuOpen}
        anchorEl={anchorEl}
        isFreeAccount={isFreeAccount}
        onClose={handleMenuClose}
        onClickHome={handleOpenHome}
        onClickLogOut={handleMenuLogOut}
      />
    </div>
  );
};
export default connect(mapStateToProps, mapDispatchToProps)(Header);
