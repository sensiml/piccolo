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

"use strict";(self.webpackChunksensiml_web=self.webpackChunksensiml_web||[]).push([[47],{1577:(e,t,r)=>{r.d(t,{A:()=>h});r(65043);var a=r(68903),s=r(85865),i=r(96446),n=r(69120),l=r(7478),o=r(98424),c=r(6011),d=r(34294),u=r(70579);const h=e=>{let{title:t,subtitle:r,onClickBack:h,actionsBtns:p,turncateLenght:m=0}=e;const x=(0,l.A)((e=>({panelWrapper:{padding:"0.75rem 1rem"},textWrapper:{display:"flex",alignItems:"center"},actionWrapper:{display:"flex",alignItems:"center",justifyContent:"flex-end",gap:e.spacing(.5),marginLeft:"auto"},stepperBackButton:{marginRight:e.spacing(2)},titleRoot:{fontSize:e.spacing(2.5)}})))();return(0,u.jsx)(c.W,{children:(0,u.jsxs)(a.Ay,{container:!0,className:x.panelWrapper,children:[(0,u.jsxs)(a.Ay,{item:!0,className:x.textWrapper,children:[h?(0,u.jsx)(d.tA,{className:x.stepperBackButton,onClick:h,color:"primary",size:"small",children:(0,u.jsx)(n.A,{})}):null,(0,u.jsx)(s.A,{variant:"h2",classes:{root:x.titleRoot},children:t&&(0,o.Ud)(t,m)}),(0,u.jsx)(i.A,{alignItems:"center",ml:2,children:r})]}),(0,u.jsx)(a.Ay,{item:!0,className:x.actionWrapper,children:p})]})})}},29299:(e,t,r)=>{r.d(t,{A:()=>z});var a=r(97508),s=r(27802),i=r(65043),n=r(53536),l=r.n(n),o=r(7426),c=r(91688),d=r(77739),u=r(17392),h=r(1995),p=r(12220),m=r(81637),x=r(95540),A=r(63471),f=r(72126),y=r(5259),j=r(75882),v=r(43024),b=r(96446),g=r(69322),C=r(45119),S=r(1980),E=r(12490),k=r(7478);const D=()=>(0,k.A)((e=>({statusBox:{padding:"0.25rem 0.5rem",border:"2px solid ".concat(e.palette.notSelected.light),borderRadius:"4px",display:"flex",alignItems:"center",justifyContent:"flex-start",color:"gray",textTransform:"uppercase",width:e.spacing(14),gridGap:e.spacing(1)},statusBoxCached:{borderColor:e.palette.success.light,color:e.palette.success.light},statusBoxBuilding:{borderColor:e.palette.primary.main,color:e.palette.primary.main},statusBoxFailed:{borderColor:e.palette.error.main,color:e.palette.error.main}})))();var R=r(70579);const w=e=>{let{cacheStatus:t}=e;const{t:r}=(0,o.B)("queries"),a=D();return(0,R.jsx)(d.A,{title:(()=>{switch(t){case E.O.CACHED:return r("cache.cache");case E.O.BUILDING:return r("cache.building-cache");case E.O.FAILED:return r("cache.failed-building-cache");default:return r("cache.no-cache")}})(),children:(0,R.jsxs)(b.A,{className:(0,v.A)(a.statusBox,{[a.statusBoxCached]:t===E.O.CACHED,[a.statusBoxBuilding]:t===E.O.BUILDING,[a.statusBoxFailed]:t===E.O.FAILED}),children:[(()=>{switch(t){case E.O.CACHED:return(0,R.jsx)(C.A,{});case E.O.BUILDING:return(0,R.jsx)(g.A,{});default:return(0,R.jsx)(S.A,{})}})()," ",t||r("cache.no-cache-status-text")]})})};var N=r(41104),I=r(52437),P=r(95004),_=r(5011),T=r(97111),L=r(33206),U=r(6011),O=r(34294);const B=()=>(0,k.A)((e=>({...e.common,root:{flexGrow:1},backdrop:{zIndex:e.zIndex.drawer+1,color:"#fff"}})))(),M=e=>{let{onUpdateProjectAction:t,queries:r,selectedProject:a,queryCacheStatusData:s,loadQueries:n,deleteQuery:v,setSelectedQuery:b,buildQueryCache:g,loadQueryCacheStatus:C,clearQueryCacheStatus:S}=e;const{t:k}=(0,o.B)("queries"),D=B(),M=(0,c.useHistory)(),[Q,z]=(0,i.useState)([]),[H,q]=(0,i.useState)(!1),[F,$]=(0,i.useState)(!1),[W,X]=(0,i.useState)(""),[G,Y]=(0,i.useState)("success"),[Z,V]=(0,i.useState)(!1),[J,K]=(0,i.useState)([]),[ee,te]=(0,i.useState)(""),[re,ae]=(0,i.useState)(null),[se,ie]=(0,i.useState)(""),ne=(0,i.useMemo)((()=>null!==J&&void 0!==J&&J.length?k("table.dialog-delete-multi-text",{count:null===J||void 0===J?void 0:J.length}):k("table.dialog-delete-text",{selectedQueryName:re})),[re,J]),le=(0,i.useMemo)((()=>l().isEmpty(J)),[J]),oe=(0,i.useMemo)((()=>l().union(J,[ee]).filter((e=>e))),[J,ee]);(0,i.useEffect)((()=>{r.data&&r.data.length>0&&r.data.forEach((e=>{e.columnList=e.columns.join(" "),e.query_segments=null==(null===e||void 0===e?void 0:e.summary_statistics)?"":e.summary_statistics.total_segments})),se||(r.data=N.A.sortObjects(r.data||[{}],"last_modified_at",!1,"dsc")),z(r)}),[r]),(0,L.$$)((async()=>{await C(a,se)}),se?5e3:null),(0,i.useEffect)((()=>{void 0!==s.build_status&&s.build_status!==E.O.BUILDING&&s.build_status!==E.O.NOT_BUILT&&(ie(""),n(a))}),[s]),(0,i.useEffect)((()=>(n(a),()=>S())),[]);const ce=(e,t)=>{b(t),M.push((0,c.generatePath)(T.bw.MAIN.DATA_EXPLORER.child.QUERY_DETAILS_SCREEN.path,{projectUUID:a,queryUUID:t}))},de=(e,t)=>{"clickaway"!==t&&$(!1)},ue=(e,t,r)=>{ae(r),te(t),q(!0)},he=(e,t)=>{X(t),Y(e),$(!0)},pe=e=>N.A.convertToLocalDateTime(e),me=[{title:"Name",field:"name",primary:!0,sortable:!0,type:I.$.Text,filterable:!0,render:(e,t)=>(0,R.jsx)(_.H,{color:"primary",onClick:e=>ce(0,t.uuid),tooltipTitle:"Open ".concat(e),children:e})},{title:"Columns",field:"columnList",sortable:!0,type:I.$.Text,filterable:!0},{title:"Filter",field:"metadata_filter",sortable:!0,type:I.$.Text,filterable:!0},{title:"Segments",field:"query_segments",sortable:!0,type:I.$.Text,filterable:!0},{title:"Last Modified",field:"last_modified",sortable:!0,type:I.$.DateTime,filterable:!0,render:pe},{title:"Created Date",field:"created_at",sortable:!0,type:I.$.DateTime,filterable:!0,render:e=>e.includes("z")&&e.includes("Z")?pe(e):pe("".concat(e,"z"))},{title:"UUID",field:"uuid",sortable:!0,type:I.$.Text,filterable:!0},{title:"Status",field:"task_status",sortable:!0,type:I.$.Text,filterable:!0,render:(e,t)=>(0,R.jsx)(w,{cacheStatus:t.task_status})},{title:"Rebuild",field:"uuid",render:(e,t)=>(0,R.jsx)(d.A,{title:"Build Cache",children:(0,R.jsx)(u.A,{variant:"contained",color:"primary",size:"small",onClick:t=>(async(e,t)=>{try{await g(a,t),ie(t)}catch(r){he("error",r.message)}})(0,e),disabled:Boolean(se),children:(0,R.jsx)(f.A,{className:se&&e===se})})})},{title:"Manage",field:"uuid",render:e=>(0,R.jsx)(d.A,{title:"Manage Query",children:(0,R.jsx)(u.A,{variant:"contained",color:"primary",size:"small",onClick:t=>ce(0,e),children:(0,R.jsx)(x.A,{})})})},{title:"Delete",field:"uuid",render:(e,t)=>(0,R.jsx)(d.A,{title:"Delete Query",children:(0,R.jsx)(u.A,{variant:"contained",color:"primary",size:"small",disabled:!le,onClick:r=>ue(0,e,t.name),children:(0,R.jsx)(A.A,{})})})}],xe={rowsPerPage:25,rowsPerPageOptions:[5,10,25,50,100,"All"],showPagination:!0,applyFilters:!0,isShowSelection:!0,selectionField:"uuid",onSelectInTable:e=>{K(e)},noContentText:"No Queries",excludePrimaryFromDetails:!0,isDarkHeader:!0};return(0,R.jsxs)(R.Fragment,{children:[(0,R.jsx)(U.f,{title:k("table.title"),onRefresh:()=>n(a),ActionComponent:(0,R.jsx)(R.Fragment,{children:(0,R.jsx)(O.U,{variant:"outlined",color:"primary",onClick:()=>ue(),tooltip:k("Delete Query"),text:k("Delete"),icon:(0,R.jsx)(A.A,{}),disabled:le,className:D.mr1})})}),(0,R.jsx)(y.A,{tableId:"queriesTable",tableColumns:me,tableData:Q,tableOptions:xe}),(0,R.jsx)(P.Z,{isOpen:H,title:k("table.dialog-delete-title"),text:ne,onConfirm:async()=>{const e=[];V(!0),q(!1);for(const t of oe){const r=await v(a,t);"error"===r.status?(he("error",r.details),V(!1)):e.push(t)}e.includes(ee)&&te(""),l().isEmpty(J)||K(J.filter((t=>!e.includes(t)))),V(!1),n(a),t(),l().isEmpty(e)||he("success",k("table.msg-success-delete",{count:null===e||void 0===e?void 0:e.length}))},onCancel:()=>{q(!1)},cancelText:k("dialog-confirm-delete.cancel"),confirmText:k("dialog-confirm-delete.delete")}),(0,R.jsx)(h.A,{anchorOrigin:{vertical:"top",horizontal:"right"},open:F,autoHideDuration:2e3,onClose:de,children:(0,R.jsx)(j.A,{onClose:de,variant:G,message:W})}),(0,R.jsx)(p.A,{className:D.backdrop,open:Z,children:(0,R.jsx)(m.A,{size:100})})]})};const Q={loadQueries:s.P6,deleteQuery:s.yN,setSelectedQuery:s.iZ,buildQueryCache:s.$1,loadQueryCacheStatus:s.lw,clearQueryCacheStatus:s.QC},z=(0,a.Ng)((function(e){return{queries:e.queries.queryList,selectedProject:e.projects.selectedProject.uuid,queryCacheStatusData:e.queries.queryCacheStatus.data||{}}}),Q)(M)},5011:(e,t,r)=>{r.d(t,{H:()=>o});r(65043);var a=r(77739),s=r(88446),i=r(7478);const n=()=>(0,i.A)((e=>({...e.common,baseLink:{color:e.palette.primary.main,textDecoration:"none","&:hover":{textDecoration:"none",cursor:"pointer",color:e.palette.primary.dark}}})))();var l=r(70579);const o=e=>{let{children:t,tooltipTitle:r,...i}=e;const o=n();return(0,l.jsx)(a.A,{title:r,children:(0,l.jsx)(s.A,{...i,className:o.baseLink,children:t})})}},64047:(e,t,r)=>{r.r(t),r.d(t,{default:()=>E});var a=r(97508),s=r(65043),i=r(69986),n=r(91688),l=r(96446),o=r(97111),c=r(27802),d=r(29299),u=r(1577),h=r(22505),p=r(33206),m=r(34815),x=r(34294),A=r(70579);const f=()=>{const{projectUUID:e}=(0,n.useParams)(),t=(0,n.useHistory)(),[r,a]=(0,s.useState)(!1);(0,p.G4)((e=>{a(e.innerWidth<m.xp.WIDTH_FOR_SHORT_TEXT)}));return(0,A.jsxs)(A.Fragment,{children:[(0,A.jsx)(l.A,{mb:2,children:(0,A.jsx)(u.A,{title:"Data Explorer",actionsBtns:(0,A.jsx)(A.Fragment,{children:(0,A.jsx)(x.bw,{variant:"outlined",color:"primary",onClick:()=>{t.push({pathname:(0,n.generatePath)(o.bw.MAIN.DATA_EXPLORER.child.QUERY_CREATE_SCREEN.path,{projectUUID:e})})},isShort:r,tooltip:"Create a new query",text:"Create Query",icon:(0,A.jsx)(h.A,{})})})})}),(0,A.jsx)(l.A,{children:(0,A.jsx)(d.A,{onUpdateProjectAction:()=>{t.push({pathname:(0,n.generatePath)(o.bw.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path,{projectUUID:e})})}})})]})},y={loadQueries:c.P6},j=(0,a.Ng)((()=>({})),y)(f),v=s.createContext();var b=r(81131);const g=(0,s.lazy)((()=>Promise.all([r.e(357),r.e(976),r.e(200),r.e(526)]).then(r.bind(r,89526)))),C=(0,s.lazy)((()=>Promise.all([r.e(357),r.e(976),r.e(200),r.e(346)]).then(r.bind(r,99346)))),S=()=>{const{projectUUID:e}=(0,n.useParams)();return(0,A.jsx)(i.A,{children:(0,A.jsx)(l.A,{children:(0,A.jsxs)(n.Switch,{children:[(0,A.jsx)(n.Route,{path:o.bw.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path,children:(0,A.jsx)(v.Provider,{children:(0,A.jsx)(j,{})})}),(0,A.jsx)(n.Route,{path:o.bw.MAIN.DATA_EXPLORER.child.QUERY_DETAILS_SCREEN.path,children:(0,A.jsx)(v.Provider,{children:(0,A.jsx)(s.Suspense,{fallback:(0,A.jsx)(b.HE,{isOpen:!0}),children:(0,A.jsx)(g,{})})})}),(0,A.jsx)(n.Route,{path:o.bw.MAIN.DATA_EXPLORER.child.QUERY_CREATE_SCREEN.path,children:(0,A.jsx)(v.Provider,{children:(0,A.jsx)(s.Suspense,{fallback:(0,A.jsx)(b.HE,{isOpen:!0}),children:(0,A.jsx)(C,{})})})}),(0,A.jsx)(n.Route,{children:(0,A.jsx)(n.Redirect,{from:o.bw.MAIN.DATA_EXPLORER.path,to:{pathname:(0,n.generatePath)(o.bw.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path,{projectUUID:e})}})})]})})})},E=(0,a.Ng)(null,null)(S)},22505:(e,t,r)=>{var a=r(24994);t.A=void 0;var s=a(r(40039)),i=r(70579);t.A=(0,s.default)((0,i.jsx)("path",{d:"M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"}),"Add")},69120:(e,t,r)=>{var a=r(24994);t.A=void 0;var s=a(r(40039)),i=r(70579);t.A=(0,s.default)((0,i.jsx)("path",{d:"M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20z"}),"ArrowBack")},45119:(e,t,r)=>{var a=r(24994);t.A=void 0;var s=a(r(40039)),i=r(70579);t.A=(0,s.default)((0,i.jsx)("path",{d:"M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"}),"Done")},95540:(e,t,r)=>{var a=r(24994);t.A=void 0;var s=a(r(40039)),i=r(70579);t.A=(0,s.default)((0,i.jsx)("path",{d:"M3 17.25V21h3.75L17.81 9.94l-3.75-3.75zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.9959.9959 0 0 0-1.41 0l-1.83 1.83 3.75 3.75z"}),"Edit")},1980:(e,t,r)=>{var a=r(24994);t.A=void 0;var s=a(r(40039)),i=r(70579);t.A=(0,s.default)((0,i.jsx)("path",{d:"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2m0 18c-4.42 0-8-3.58-8-8 0-1.85.63-3.55 1.69-4.9L16.9 18.31C15.55 19.37 13.85 20 12 20m6.31-3.1L7.1 5.69C8.45 4.63 10.15 4 12 4c4.42 0 8 3.58 8 8 0 1.85-.63 3.55-1.69 4.9"}),"NotInterested")},81637:(e,t,r)=>{r.d(t,{A:()=>P});var a=r(57528),s=r(98587),i=r(58168),n=r(65043),l=r(69292),o=r(68606),c=r(59626),d=r(6803),u=r(72876),h=r(34535),p=r(57056),m=r(32400);function x(e){return(0,m.Ay)("MuiCircularProgress",e)}(0,p.A)("MuiCircularProgress",["root","determinate","indeterminate","colorPrimary","colorSecondary","svg","circle","circleDeterminate","circleIndeterminate","circleDisableShrink"]);var A,f,y,j,v=r(70579);const b=["className","color","disableShrink","size","style","thickness","value","variant"];let g,C,S,E;const k=44,D=(0,c.i7)(g||(g=A||(A=(0,a.A)(["\n  0% {\n    transform: rotate(0deg);\n  }\n\n  100% {\n    transform: rotate(360deg);\n  }\n"])))),R=(0,c.i7)(C||(C=f||(f=(0,a.A)(["\n  0% {\n    stroke-dasharray: 1px, 200px;\n    stroke-dashoffset: 0;\n  }\n\n  50% {\n    stroke-dasharray: 100px, 200px;\n    stroke-dashoffset: -15px;\n  }\n\n  100% {\n    stroke-dasharray: 100px, 200px;\n    stroke-dashoffset: -125px;\n  }\n"])))),w=(0,h.Ay)("span",{name:"MuiCircularProgress",slot:"Root",overridesResolver:(e,t)=>{const{ownerState:r}=e;return[t.root,t[r.variant],t["color".concat((0,d.A)(r.color))]]}})((e=>{let{ownerState:t,theme:r}=e;return(0,i.A)({display:"inline-block"},"determinate"===t.variant&&{transition:r.transitions.create("transform")},"inherit"!==t.color&&{color:(r.vars||r).palette[t.color].main})}),(e=>{let{ownerState:t}=e;return"indeterminate"===t.variant&&(0,c.AH)(S||(S=y||(y=(0,a.A)(["\n      animation: "," 1.4s linear infinite;\n    "]))),D)})),N=(0,h.Ay)("svg",{name:"MuiCircularProgress",slot:"Svg",overridesResolver:(e,t)=>t.svg})({display:"block"}),I=(0,h.Ay)("circle",{name:"MuiCircularProgress",slot:"Circle",overridesResolver:(e,t)=>{const{ownerState:r}=e;return[t.circle,t["circle".concat((0,d.A)(r.variant))],r.disableShrink&&t.circleDisableShrink]}})((e=>{let{ownerState:t,theme:r}=e;return(0,i.A)({stroke:"currentColor"},"determinate"===t.variant&&{transition:r.transitions.create("stroke-dashoffset")},"indeterminate"===t.variant&&{strokeDasharray:"80px, 200px",strokeDashoffset:0})}),(e=>{let{ownerState:t}=e;return"indeterminate"===t.variant&&!t.disableShrink&&(0,c.AH)(E||(E=j||(j=(0,a.A)(["\n      animation: "," 1.4s ease-in-out infinite;\n    "]))),R)})),P=n.forwardRef((function(e,t){const r=(0,u.A)({props:e,name:"MuiCircularProgress"}),{className:a,color:n="primary",disableShrink:c=!1,size:h=40,style:p,thickness:m=3.6,value:A=0,variant:f="indeterminate"}=r,y=(0,s.A)(r,b),j=(0,i.A)({},r,{color:n,disableShrink:c,size:h,thickness:m,value:A,variant:f}),g=(e=>{const{classes:t,variant:r,color:a,disableShrink:s}=e,i={root:["root",r,"color".concat((0,d.A)(a))],svg:["svg"],circle:["circle","circle".concat((0,d.A)(r)),s&&"circleDisableShrink"]};return(0,o.A)(i,x,t)})(j),C={},S={},E={};if("determinate"===f){const e=2*Math.PI*((k-m)/2);C.strokeDasharray=e.toFixed(3),E["aria-valuenow"]=Math.round(A),C.strokeDashoffset="".concat(((100-A)/100*e).toFixed(3),"px"),S.transform="rotate(-90deg)"}return(0,v.jsx)(w,(0,i.A)({className:(0,l.A)(g.root,a),style:(0,i.A)({width:h,height:h},S,p),ownerState:j,ref:t,role:"progressbar"},E,y,{children:(0,v.jsx)(N,{className:g.svg,ownerState:j,viewBox:"".concat(22," ").concat(22," ").concat(k," ").concat(k),children:(0,v.jsx)(I,{className:g.circle,style:C,ownerState:j,cx:k,cy:k,r:(k-m)/2,fill:"none",strokeWidth:m})})}))}))}}]);
//# sourceMappingURL=47.26b8fe47.chunk.js.map