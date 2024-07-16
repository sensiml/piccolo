"use strict";(self.webpackChunksensiml_web=self.webpackChunksensiml_web||[]).push([[635],{94635:(e,t,a)=>{a.r(t),a.d(t,{default:()=>ae});var l=a(97508),i=a(20433),r=a(65043);const o=e=>{var t,a,l;return e.projects.lastSelectedProjects["".concat(null===(t=e.auth)||void 0===t||null===(a=t.teamInfo)||void 0===a?void 0:a.team,"-").concat(null===e||void 0===e||null===(l=e.auth)||void 0===l?void 0:l.userId)]};var n=a(53536),s=a.n(n),c=a(7426),d=a(77739),p=a(85865),u=a(17392),m=a(88446),h=a(96446),j=a(68903),x=a(63336),g=a(1995),v=a(90555),f=a(63471),b=a(91688),A=a(22505),y=a(67500),S=a(75882),P=a(7478);const C=e=>e<80?"#81c784":e<100?"#ef6c00":"#d50000",N=e=>e<80?"#000000":"#FFFFFF",w=e=>(0,P.A)((()=>({capsuleCell:{height:15,display:"inline-block"},firstSection:{borderRadius:e>90?"5px 5px 5px 5px":"5px 0px 0px 5px",padding:3,display:0===e?"none":"inline-block",background:C(e),width:"".concat(e>90?91:e,"%")},secondSection:{borderRadius:0===e?"5px 5px 5px 5px":"0px 5px 5px 0px",padding:e>90?0:2,background:"#FFFFF",border:"1px solid",borderColor:C(e),display:e>90?"none":"inline-block",width:"".concat(e>90?1:100-e-15,"%")},floater:{top:2,clear:"both",position:"absolute",left:10,color:N(e)},container:{minWidth:120,display:"inline-block"},mainContainer:{position:"relative"}})))();var F=a(70579);const k=e=>{let{value:t,highLimit:a}=e;const l=w(a&&a>0?t<=a?t/a*100:100:0);return(0,F.jsxs)("div",{className:l.mainContainer,children:[(0,F.jsx)("span",{className:l.floater,children:"".concat(t," of ").concat(a)}),(0,F.jsxs)("span",{className:l.container,children:[(0,F.jsx)("span",{className:"".concat(l.capsuleCell," ").concat(l.firstSection)}),(0,F.jsx)("span",{className:"".concat(l.capsuleCell," ").concat(l.secondSection)})]})]})};var T=a(67784),D=a(51787),E=a(11906),_=a(48625),I=a(66360),L=a(69986);const W=()=>(0,P.A)((e=>({searchWrapper:{display:"flex",alignItems:"center",justifyContent:"space-between",padding:e.spacing(2)},searchTextField:{width:"100%"},refreshButton:{padding:e.spacing(2),marginLeft:"1rem"}})))(),z=e=>{let{setSearchText:t,resetHandler:a}=e;const[l,i]=(0,r.useState)(""),o=W();return(0,F.jsx)(L.A,{children:(0,F.jsxs)(h.A,{className:o.searchWrapper,children:[(0,F.jsx)(T.A,{variant:"outlined",id:"txtProjectSearch",className:o.searchTextField,label:"Project Search",onChange:e=>{i(e.target.value),t(e.target.value)},value:l,InputProps:{endAdornment:(0,F.jsx)(D.A,{position:"end",children:(0,F.jsx)(u.A,{size:"large",children:(0,F.jsx)(I.A,{})})})}}),(0,F.jsx)(d.A,{title:"Refresh Projects",children:(0,F.jsx)(E.A,{className:o.refreshButton,variant:"contained",color:"primary",size:"medium",onClick:()=>{i(""),a()},children:(0,F.jsx)(_.A,{})})})]})})};var M=a(5259),R=a(67254),B=a(4172);const O=e=>{let{isOpen:t,defaultName:a,title:l="",description:i="",existingNames:o=[],validationError:n,onClose:d,onSubmit:u}=e;const{t:m}=(0,c.B)("components"),j=(0,P.A)((e=>({createDialogTitle:{marginBottom:e.spacing(2),textAlign:"center"},formWrap:{width:"100%",display:"flex",flexDirection:"column",marginTop:e.spacing(3),marginBottom:e.spacing(2)}})))(),[x,g]=(0,r.useState)(""),[v,f]=(0,r.useState)(),b=(0,r.useMemo)((()=>!x),[x]),A=()=>{d()};return(0,r.useEffect)((()=>{n&&f(n)}),[n]),(0,r.useEffect)((()=>()=>f("")),[]),(0,r.useEffect)((()=>()=>g("")),[]),(0,F.jsx)(B.A,{disableEscapeKeyDown:!0,isOpen:t,onClose:A,"aria-labelledby":l,actionsComponent:(0,F.jsxs)(F.Fragment,{children:[(0,F.jsx)(E.A,{onClick:A,color:"primary",variant:"outlined",fullWidth:!0,children:m("dialog-form-project.btn-action-cancel")}),(0,F.jsx)(E.A,{onClick:()=>{(function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"";return s().isEmpty(o.find((t=>s().toLower(s().trim(e))===s().toLower(s().trim(t)))))?[]:(f(m("dialog-form-project.validation-error-duplicate",{name:e})),!1)})(x)&&u(x)},color:"primary",variant:"contained",disabled:b,fullWidth:!0,children:m("dialog-form-project.btn-action-save")})]}),children:(0,F.jsxs)(h.A,{children:[l?(0,F.jsx)(p.A,{variant:"h2",className:j.createDialogTitle,children:l}):null,i?(0,F.jsx)(h.A,{mt:1,mb:2,children:(0,F.jsx)(R.A,{severity:"info",children:i})}):null,(0,F.jsx)(h.A,{className:j.formWrap,children:(0,F.jsx)(T.A,{error:Boolean(v),helperText:v,autoFocus:!0,id:"projectName",label:m("dialog-form-project.label-name"),variant:"outlined",required:!0,defaultValue:a,onChange:e=>{var t;f(""),g(null===e||void 0===e||null===(t=e.target)||void 0===t?void 0:t.value)},fullWidth:!0})})]})})};O.defaultProps={onSubmit:()=>{},onClose:()=>{}};const H=O;var $=a(53827),V=a(95004),U=a(6011),Y=a(34294),q=a(97111),J=a(83271);const G=()=>(0,P.A)((e=>{var t;return{...e.common,searchWrapper:{marginBottom:e.spacing(2)},segmenterTypography:{padding:e.spacing(1)},segmenterTooltip:{backgroundColor:e.palette.common.white,color:"rgba(0, 0, 0, 0.87)",border:"1px solid #dadde9",maxWidth:"none",boxShadow:e.shadows[5],margin:1},lastProjectWrapper:{marginTop:e.spacing(2),padding:e.spacing(2)},lastProjectTitle:{fontSize:e.spacing(3),fontWeight:600,color:null===(t=e.palette.notSelected)||void 0===t?void 0:t.main}}}))(),K=e=>e?e.map((e=>({...e,created_at:e.created_at?new Date(e.created_at).toLocaleDateString():null}))):e,Q=e=>{let{projectData:t,lastSelectedProject:a,selectedProject:l,userId:i,teamInfo:o,setSelectedProject:n,setLastSelectedProject:P,createProject:C,deleteProject:N,loadProjects:w}=e;const{t:T}=(0,c.B)("projects"),D=G(),E=(0,b.useHistory)(),[_]=(0,r.useState)(10),[I,L]=(0,r.useState)(K(t.data)),[W,R]=r.useState(!1),[B,O]=r.useState(!1),[Q,Z]=r.useState(""),[X,ee]=r.useState("success"),[te,ae]=(0,r.useState)(""),[le,ie]=(0,r.useState)(""),[re,oe]=(0,r.useState)(!1),[ne,se]=(0,r.useState)(""),ce=(0,r.useMemo)((()=>s().isEmpty(null===t||void 0===t?void 0:t.data)?[]:t.data.map((e=>e.name))),[t]),de=s().debounce((e=>{return a=e,void(t.data&&t.data.length>0&&L(K(t.data.filter((e=>new RegExp(a,"i").test(e.name))))));var a}),200),pe=e=>{de(e)},ue=(e,a)=>{(async e=>{if(""===e)return;await n(e);const a=t.data&&t.data.find((t=>t.uuid===e));P(a,null===o||void 0===o?void 0:o.team,i),y.A.logInfo("","open_project",{total_files:(null===a||void 0===a?void 0:a.files)||0,total_segments:(null===a||void 0===a?void 0:a.segments)||0,total_knowledge_packs:(null===a||void 0===a?void 0:a.models)||0,project_uuid:null===a||void 0===a?void 0:a.uuid,project_name:null===a||void 0===a?void 0:a.name}),E.push((0,b.generatePath)(q.bw.MAIN.PROJECT_SUMMARY.path,{projectUUID:e}))})(a)};(0,r.useEffect)((()=>{(async()=>{s().isEmpty(t.data)&&await w()})()}),[]),(0,r.useEffect)((()=>{L(K(t.data))}),[t]);const me=e=>e||0,he=(e,t)=>{"clickaway"!==t&&O(!1)},je=(e,t)=>{Z(t),ee(e),O(!0)},xe=e=>{ne&&se(""),oe(e)},ge=[{title:"",field:"uuid",render:e=>(0,F.jsx)(d.A,{title:"Open Project..",children:(0,F.jsx)(u.A,{variant:"contained",color:"primary",size:"small",onClick:t=>ue(0,e),children:(0,F.jsx)(v.A,{})})})},{title:"Name",field:"name",primary:!0,sortable:!0,type:$.$.Text,filterable:!0},{title:"Files",field:"files",render:me,sortable:!0,type:$.$.Numeric,filterable:!0},{title:"Pipelines",field:"pipelines",render:me,sortable:!0,type:$.$.Numeric,filterable:!0},{title:"Size (MB)",field:"size_mb",render:me,type:$.$.Numeric,sortable:!0,filterable:!0},{title:"Queries",field:"queries",render:me,sortable:!0,type:$.$.Numeric,filterable:!0},{title:"Models",field:"models",render:me,sortable:!0,type:$.$.Numeric,filterable:!0},{title:"Segments",field:"segments",render:e=>{const t=e||0;return o&&"STARTER"===o.subscription?(0,F.jsx)(d.A,{placement:"bottom",classes:{tooltip:D.segmenterTooltip},title:(0,F.jsxs)(F.Fragment,{children:[" ",(0,F.jsx)(p.A,{className:D.segmenterTypography,children:(0,F.jsx)("pre",{style:{fontFamily:"inherit"},children:"Starter editions are limited to 2500 labeled segments per project."})})]}),children:(0,F.jsxs)("span",{children:[" ",(0,F.jsx)(k,{value:t,highLimit:2500})]})}):t},sortable:!0,type:$.$.Numeric,filterable:!0},{title:"Created Date",field:"created_at",type:"date",render:me,sortable:!0,filterable:!0},{title:"Delete",field:"uuid",render:(e,t)=>(0,F.jsx)(d.A,{title:"Delete Project.",children:(0,F.jsx)(u.A,{variant:"contained",color:"primary",size:"small",onClick:a=>{return l=e,i=t.name,ie(i),ae(l),void R(!0);var l,i},children:(0,F.jsx)(f.A,{})})})}],ve={isDarkHeader:!0,rowsPerPage:_,showPagination:!0,noContentText:(0,F.jsxs)(F.Fragment,{children:["Welcome to the SensiML Analytics Toolkit. Follow the"," ",(0,F.jsx)(m.A,{target:"_blank",href:J.Jp,children:"Getting Started guide"})," ","to learn how to build your first application."]}),excludePrimaryFromDetails:!0,rowsPerPageOptions:[5,10,25,50,100,"All"],applyFilters:!0,onRowDoubleClick:(e,t)=>{ue(0,t.uuid,t.name)}};return(0,F.jsx)(h.A,{className:D.root,children:(0,F.jsxs)(j.Ay,{container:!0,spacing:0,children:[(0,F.jsx)(j.Ay,{item:!0,xs:12,className:D.searchWrapper,children:(0,F.jsx)(x.A,{elevation:0,children:(0,F.jsx)(z,{setSearchText:pe,resetHandler:()=>{pe(""),w()}})})}),(0,F.jsxs)(j.Ay,{item:!0,xs:12,className:D.loadedElement,children:[(0,F.jsx)(U.f,{title:T("table.title"),ActionComponent:(0,F.jsx)(F.Fragment,{children:(0,F.jsx)(Y.U,{variant:"outlined",color:"primary",onClick:()=>xe(!0),tooltip:"Create a new project",text:T("table.btn-create"),icon:(0,F.jsx)(A.A,{})})})}),(0,F.jsx)(M.A,{className:"step",tableId:"projectList",tableColumns:ge,tableData:{data:I,isFetching:t.isFetching},tableOptions:ve})]}),null===a||void 0===a||!a.uuid||l.uuid||t.isFetching?null:(0,F.jsx)(j.Ay,{item:!0,xs:12,children:(0,F.jsx)(x.A,{elevation:0,className:D.lastProjectWrapper,children:(0,F.jsxs)(p.A,{variant:"h2",className:D.lastProjectTitle,children:["Last opened project:"," ",(0,F.jsx)(m.A,{underline:"hover",href:"#",onClick:e=>ue(0,null===a||void 0===a?void 0:a.uuid),children:null===a||void 0===a?void 0:a.name})]})})}),re?(0,F.jsx)(H,{title:T("table.dialog-create-title"),isOpen:re,existingNames:ce,validationError:ne,onClose:()=>xe(!1),onSubmit:async e=>{try{await C(e),xe(!1),je("success",T("table.success-msg-create-project",{name:e}))}catch(t){se(t.message)}}}):null,(0,F.jsxs)(j.Ay,{item:!0,xs:12,children:[(0,F.jsx)(V.Z,{isOpen:W,title:T("table.dialog-delete-title"),text:T("table.dialog-delete-text",{deletingProjectName:le}),onConfirm:async()=>{R(!1);try{await N(te)}catch(e){let t="Failed to deleted ".concat(le);return e&&e.response&&e.response.status&&403===e.response.status&&(t="Your account does not have permission to delete a Project."),je("error",t),void await w()}je("success",T("table.success-msg-delete-project",{name:le}))},onCancel:()=>{R(!1)},cancelText:T("dialog-confirm-delete.cancel"),confirmText:T("dialog-confirm-delete.delete")}),(0,F.jsx)(g.A,{anchorOrigin:{vertical:"top",horizontal:"right"},open:B,autoHideDuration:2e3,onClose:he,children:(0,F.jsx)(S.A,{onClose:he,variant:X,message:Q})})]})]})})},Z={setSelectedProject:i.NR,setLastSelectedProject:i.nY,createProject:i.gA,deleteProject:i.xx,loadProjects:i.RT},X=(0,l.Ng)((e=>({projectData:e.projects.projectList,teamInfo:e.auth.teamInfo,userId:e.auth.userId,lastSelectedProject:o(e),selectedProject:e.projects.selectedProject})),Z)(Q),ee=e=>{let{setSelectedProject:t,clearProjectSelectedData:a}=e;return(0,r.useEffect)((()=>{t(""),a()}),[]),(0,F.jsx)(X,{})},te={setSelectedProject:i.NR,clearProjectSelectedData:i.Io},ae=(0,l.Ng)((()=>({})),te)(ee)},22505:(e,t,a)=>{var l=a(24994);t.A=void 0;var i=l(a(40039)),r=a(70579);t.A=(0,i.default)((0,r.jsx)("path",{d:"M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z"}),"Add")},90555:(e,t,a)=>{var l=a(24994);t.A=void 0;var i=l(a(40039)),r=a(70579);t.A=(0,i.default)((0,r.jsx)("path",{d:"M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3z"}),"Launch")},66360:(e,t,a)=>{var l=a(24994);t.A=void 0;var i=l(a(40039)),r=a(70579);t.A=(0,i.default)((0,r.jsx)("path",{d:"M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14"}),"Search")}}]);
//# sourceMappingURL=635.5a8185dc.chunk.js.map