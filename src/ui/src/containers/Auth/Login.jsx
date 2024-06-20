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

/* eslint-disable jsx-a11y/anchor-is-valid */
import React, { useState, useEffect } from "react";

import {
  Button,
  Card,
  CardContent,
  Checkbox,
  FormControl,
  FormControlLabel,
  Grid,
  Hidden,
  InputAdornment,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  InputLabel,
  TextField,
  Paper,
  Typography,
} from "@mui/material";

import EmailIcon from "@mui/icons-material/Email";
import LockIcon from "@mui/icons-material/Lock";
import CheckIcon from "@mui/icons-material/Check";

import { useTranslation } from "react-i18next";
import { useCookies } from "react-cookie";
import { useRouterSearchParams } from "hooks";

import logoImg from "assets/images/logo-transparent.png";
import responsiveViewImg from "assets/images/responsive-view.png";

import { UISnackBar } from "components/UISnackBar";

import useStyles from "./AuthStyles";

const LoginForm = ({ logIn, isDisableLogin }) => {
  const { t } = useTranslation("auth");
  const classes = useStyles();
  const [searchParams, removeSearchParams] = useRouterSearchParams();
  const [cookies, setCookie, removeCookie] = useCookies(["app.sensiml.cloud"]);
  const [email, setEmail] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [error, setError] = useState(null);

  // eslint-disable-next-line no-shadow
  const performLogin = async (email, password) => {
    setError("");
    setCookie("remember", rememberMe, { path: "/" });
    if (rememberMe === true) {
      setCookie("email_address", email, { path: "/" });
    }

    try {
      await logIn({ email, password });
    } catch (e) {
      setError(t(e.message));
    }
  };

  useEffect(() => {
    // If the query string has demo in it then auto login using the
    // demo account.
    const params = new URLSearchParams(window.location.search.slice(1));
    if (params && params.has("demo")) {
      setEmail(process.env.REACT_APP_DEMO_ACCOUNT);
      setPassword(process.env.REACT_APP_DEMO_PASSWORD);
      performLogin(process.env.REACT_APP_DEMO_ACCOUNT, process.env.REACT_APP_DEMO_PASSWORD);
    }

    const remember = cookies.remember === "true";
    const emailAddress = cookies.email_address;
    setRememberMe(remember);
    if (remember === true && emailAddress !== undefined) {
      setEmail(emailAddress);
    }
  }, []);

  useEffect(() => {
    if (searchParams.has("error")) {
      setErrorMessage(searchParams.get("error"));
    }
  }, [searchParams]);

  const handleCloseErrorMessage = () => {
    setErrorMessage("");
    if (searchParams.has("error")) {
      removeSearchParams(["error"]);
    }
  };

  const handleChange = (setField) => (event) => {
    setField(event.target.value);
    setError(false);
  };

  const handleRememberMe = (event) => {
    setRememberMe(event.target.checked);
    setCookie("remember", event.target.checked, { path: "/" });
    if (event.target.checked === false) {
      removeCookie("email_address");
    } else {
      setCookie("email_address", email, { path: "/" });
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    await performLogin(email, password);
  };

  const forgotPassword = () => {
    window.open(`${process.env.REACT_APP_API_URL}accounts/password/reset/`);
  };

  const privacyAndLegalNotice = () => {
    window.open(`${process.env.REACT_APP_MKT_URL}legal-notices/`);
  };

  const register = () => {
    window.open(`${process.env.REACT_APP_MKT_URL}plans/community-edition/`);
  };

  const learnMore = () => {
    window.open(`${process.env.REACT_APP_MKT_URL}products/?ref=web-app`);
  };

  return (
    <div className={classes.root}>
      <Grid container spacing={0} justifyContent="center" alignItems="center">
        <Grid item xs={12} lg={6} md={12}>
          <div className={classes.loginSection}>
            <Grid
              container
              spacing={0}
              justifyContent="center"
              alignItems="center"
              direction="row"
              className={classes.loginGrid}
            >
              <Grid item xs>
                <img src={logoImg} className={classes.logoImg} alt={t("img-alt-logo")} />
                <Grid container spacing={0} justifyContent="center" alignItems="center">
                  <Grid item xs={9} xl={6} lg={9} md={9}>
                    <Card className={classes.card} variant="outlined">
                      <CardContent className={classes.cardContent}>
                        {error ? (
                          <div className={classes.errorDiv}>
                            <FormControl fullWidth={true}>
                              <InputLabel id="loginError" className={classes.errorMessage}>
                                {error}
                              </InputLabel>
                            </FormControl>
                            <br />
                          </div>
                        ) : null}
                        <form onSubmit={handleLogin}>
                          <FormControl fullWidth={true}>
                            <TextField
                              label={t("label-email")}
                              value={email}
                              onChange={handleChange(setEmail)}
                              className={classes.pos}
                              autoFocus={true}
                              id="email"
                              InputProps={{
                                startAdornment: (
                                  <InputAdornment position="start">
                                    <EmailIcon color="primary" />
                                  </InputAdornment>
                                ),
                              }}
                              variant="outlined"
                            />
                          </FormControl>{" "}
                          <br />
                          <FormControl fullWidth={true}>
                            <TextField
                              label={t("label-password")}
                              type="password"
                              value={password}
                              onChange={handleChange(setPassword)}
                              className={classes.pos}
                              id="password"
                              InputProps={{
                                startAdornment: (
                                  <InputAdornment position="start">
                                    <LockIcon color="primary" />
                                  </InputAdornment>
                                ),
                              }}
                            />
                          </FormControl>{" "}
                          <br />
                          <FormControl fullWidth={true}>
                            <Button
                              type="submit"
                              variant="contained"
                              id="loginButton"
                              className={classes.loginButton}
                              color={"primary"}
                              disabled={isDisableLogin}
                            >
                              {t("btn-login")}
                            </Button>
                          </FormControl>
                          <br />
                          <Grid container direction="row">
                            <Grid item xs={6}>
                              <FormControlLabel
                                className={classes.rememberMe}
                                control={
                                  <Checkbox
                                    name="rememberme"
                                    id="rememberme"
                                    checked={rememberMe}
                                    onChange={handleRememberMe}
                                  />
                                }
                                label={
                                  <Typography
                                    className={classes.rememberMe}
                                    variant="button"
                                    color="primary"
                                  >
                                    {t("label-remember-me")}
                                  </Typography>
                                }
                              />
                            </Grid>
                            <Grid item xs={6} className={classes.forgotPassword}>
                              <Button
                                id="forgotPasswordButton"
                                size="small"
                                className={classes.textButton}
                                onClick={forgotPassword}
                                color="primary"
                              >
                                {t("link-forgot-password")}
                              </Button>
                            </Grid>
                          </Grid>
                        </form>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} className={classes.register}>
                    <Button
                      size="small"
                      id="createSensiMLIdButton"
                      className={classes.textButton}
                      onClick={register}
                      color="primary"
                    >
                      {t("link-create-account")}
                    </Button>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
          </div>
          <div className={classes.footer}>
            <Typography variant="caption" id="privacyAndCopyRight">
              <a
                href="#"
                id="privacyLink"
                title={t("link-privacy")}
                onClick={privacyAndLegalNotice}
              >
                {t("link-privacy")}
              </a>
              {` ${t("copyright", { year: new Date().getFullYear() })}`}
            </Typography>
          </div>
        </Grid>
        <Grid item lg={6}>
          <Hidden only={["xs", "sm", "md"]} implementation={"js"}>
            <div>
              <Paper square={true} elevation={0} className={classes.evalSection}>
                <Grid container spacing={0} justifyContent="center" alignItems="center">
                  <Grid item xs={12}>
                    <Typography variant="h5" id="evaluationButton">
                      {t("eval-title")}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <div className={classes.featureList}>
                      <List dense={true}>
                        <ListItem>
                          <ListItemIcon className={classes.featureListIcon}>
                            <CheckIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={t("eval-points-0")} />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon className={classes.featureListIcon}>
                            <CheckIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={t("eval-points-1")} />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon className={classes.featureListIcon}>
                            <CheckIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText primary={t("eval-points-2")} />
                        </ListItem>
                      </List>
                    </div>
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      id="freeTrialButton"
                      className={classes.evalButtons}
                      onClick={register}
                      variant="contained"
                      color="primary"
                    >
                      {t("btn-start-free-trial")}
                    </Button>
                    <Button
                      id="learnMoreButton"
                      className={classes.evalButtons}
                      onClick={learnMore}
                      variant="contained"
                      color="primary"
                    >
                      {t("btn-learn-more")}
                    </Button>
                  </Grid>
                  <Grid item xs={12}>
                    <img
                      src={responsiveViewImg}
                      alt={t("img-alt-resposible-view")}
                      className={classes.responsiveViewImg}
                    />
                  </Grid>
                </Grid>
              </Paper>
            </div>
          </Hidden>
        </Grid>
      </Grid>
      <UISnackBar
        isOpen={Boolean(errorMessage)}
        message={errorMessage}
        onClose={handleCloseErrorMessage}
        variant={"error"}
        autoHideDuration={5000}
      />
    </div>
  );
};

export default LoginForm;
