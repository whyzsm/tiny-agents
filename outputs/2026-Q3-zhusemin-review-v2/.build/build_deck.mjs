import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const root = "/Users/seminzhu/Documents/AI/tiny-agents/outputs/2026-Q3-zhusemin-review-v2";
const buildDir = path.join(root, ".build");
const renderDir = path.join(root, "rendered");
const draft = path.join(buildDir, "draft.pptx");
const final = path.join(root, "deliverables", "2026-Q3-zhusemin-review-v2.pptx");
const C = { navy:"#06283A", ink:"#12212B", teal:"#0B7A75", blue:"#1677B9", orange:"#C96A24", pale:"#F5F8FA", line:"#D7E1E7", gray:"#5C6A73", white:"#FFFFFF" };
const FONT = "PingFang SC";

function box(slide, geometry, left, top, width, height, fill="none", line="none", lineWidth=0) {
  return slide.shapes.add({geometry,position:{left,top,width,height},fill,line:{style:"solid",fill:line,width:lineWidth}});
}
function tx(slide, value, left, top, width, height, style={}) {
  const s = box(slide,"textbox",left,top,width,height);
  s.text = value;
  s.text.style = {typeface:FONT,fontSize:18,color:C.ink,...style};
  return s;
}
function bar(slide,left,top,width,color=C.line,height=2) { return box(slide,"rect",left,top,width,height,color); }
function note(slide,value) { slide.speakerNotes.text=value; slide.speakerNotes.setVisible(true); }
function foot(slide,page,dark=false) {
  const color=dark?"#BFD2D9":"#8A979F";
  tx(slide,"2026 Q3 述职汇报",72,680,260,22,{fontSize:12,color});
  tx(slide,String(page).padStart(2,"0"),1160,680,48,22,{fontSize:12,color,alignment:"right"});
}
function head(slide,kicker,title,dark=false) {
  tx(slide,kicker,72,48,360,24,{fontSize:14,bold:true,color:dark?"#8FD0D0":C.teal});
  tx(slide,title,72,82,1100,52,{fontSize:32,bold:true,color:dark?C.white:C.ink});
  bar(slide,72,148,1136,dark?"#2B5361":C.line,2);
}
function metric(slide,value,label,left,top,color,dark=false) {
  tx(slide,value,left,top,250,60,{fontSize:42,bold:true,color:dark?C.white:color});
  tx(slide,label,left,top+62,280,34,{fontSize:15,color:dark?"#BFD2D9":C.gray});
}
function pill(slide,value,left,top,width,fill,color) {
  box(slide,"roundRect",left,top,width,30,fill);
  tx(slide,value,left,top+5,width,20,{fontSize:13,bold:true,color,alignment:"center"});
}

const data = [
  {kind:"cover",notes:"开场：先给结论，再按 O1、O2、O3 展开。Q3 的重点不只是完成业务需求，也包括把项目经验沉淀成可复用的工程和 AI 能力。来源：用户提供的 Q3 OKR 材料与工作报告。"},
  {kind:"summary",notes:"先讲清三条主线，不展开仓库清单。O3 的 trunkFeeder-ui/skill 是绩效指标本身，应作为独立成果来讲。统计数字只使用已经核对过的口径。来源：Q3 OKR 材料、工作报告、trunkFeeder-ui/skill 仓库审阅。"},
  {kind:"o1",notes:"把业务交付和质量结果放在同一页，回答做了什么以及上线后怎么样。生产 BUG、线上问题闭环和测试 BUG 率指标沿用已核对的 Q3 材料。来源：Q3 O1 材料与工作报告。"},
  {kind:"timeline",notes:"用智能排班说明你参与了业务链路拆解和分期交付，重点讲从调度骨架到运营反馈的能力推进。来源：工作报告中 trunkFeeder-ui 的智能排班一期、二期内容。"},
  {kind:"o2",notes:"重点讲统一技术栈与可观测性如何服务稳定交付，不展开依赖升级细节。来源：Q3 O2 材料与工作报告。"},
  {kind:"o3",notes:"明确绑定绩效：trunkFeeder-ui/skill 是 O3 的关键成果。内容包括业务规则、设计系统、技术栈、验证清单和防幻觉约束。评测结果沿用已审阅材料中的有 Skill 100%、无 Skill 83%、差值 +17pp。来源：Q3 O3 材料、skill 文件、评测提交记录。"},
  {kind:"roles",notes:"用三个角色回答你在项目中的位置：业务交付主力、Skill 建设者、工程能力沉淀者。来源：工作报告、skill/SKILL.md、references 资料和评测记录。"},
  {kind:"challenge",notes:"用问题、处理方式、留下的能力表达难点。最后保留一个真实边界：当前校验脚本仍查找旧目录名，需要后续改成仓库根目录相对路径。来源：2026-10-13 对 trunkFeeder-ui/skill 的现场审阅与脚本运行结果。"},
  {kind:"growth",notes:"把成长落到研发视角变化：从页面交付扩展到业务建模、工程治理和 AI 工作流设计。下一步内容属于后续计划，不作为 Q3 已完成事实。来源：Q3 O3 目标、skill 仓库现状和验证结果。"},
  {kind:"closing",notes:"结束语：回到三条结论即可。若现场追问，再补充需求清单、仓库范围和 skill 文件结构。来源：Q3 OKR 材料、T-MAX 工作报告、trunkFeeder-ui/skill 仓库审阅。"}
];

function render(slide, kind, page) {
  if (kind==="cover") {
    slide.background.fill=C.navy; bar(slide,72,94,104,C.orange,5);
    tx(slide,"2026 Q3",72,140,400,42,{fontSize:23,bold:true,color:"#BFD2D9"});
    tx(slide,"述职汇报",72,194,650,100,{fontSize:56,bold:true,color:C.white});
    tx(slide,"业务交付、工程治理与 Skill 沉淀",76,314,680,42,{fontSize:24,color:"#BFD2D9"});
    tx(slide,"朱色敏  ·  00118740",76,590,420,28,{fontSize:16,color:"#BFD2D9"});
    tx(slide,"前端研发 / T-MAX",76,624,360,24,{fontSize:14,color:"#8FAAB4"});
    tx(slide,"Q3",866,190,300,190,{fontSize:164,bold:true,color:"#17475A",alignment:"center"});
    bar(slide,900,408,232,C.teal,5); tx(slide,"稳定交付的工程化沉淀",862,438,310,30,{fontSize:15,bold:true,color:"#BFD2D9",alignment:"center"}); foot(slide,page,true); return;
  }
  if (kind==="closing") {
    slide.background.fill=C.navy; bar(slide,72,154,110,C.orange,5); tx(slide,"Q3 总结",72,202,300,34,{fontSize:18,bold:true,color:"#BFD2D9"});
    tx(slide,"把交付经验\n变成可复用能力",72,258,760,150,{fontSize:54,bold:true,color:C.white});
    tx(slide,"业务交付有结果，工程建设有沉淀，Skill 建设有验证。",76,464,780,38,{fontSize:24,color:"#BFD2D9"}); tx(slide,"谢谢",956,538,190,42,{fontSize:30,bold:true,color:"#8FD0D0",alignment:"right"}); foot(slide,page,true); return;
  }
  slide.background.fill = kind==="summary"||kind==="timeline"||kind==="roles"||kind==="growth" ? C.pale : C.white;
  if (kind==="o3") slide.background.fill=C.navy;
  const dark = kind==="o3";
  const titles={
    summary:["Q3 总览","Q3 的主线，是把一次次交付变成稳定、可复用的交付能力"],
    o1:["O1 业务交付与质量","业务交付从按时完成，进一步落到上线后稳定运行"],
    timeline:["重点案例","智能排班把复杂调度规则推进到可运营的功能闭环"],
    o2:["O2 前端基建与可观测性","统一技术栈与可观测性，降低多仓库协作的维护成本"],
    o3:["O3 AI 赋能","trunkFeeder-ui/skill：把项目经验沉淀为 AI 可执行的工程资产"],
    roles:["项目角色","从业务交付到 Skill 建设，我承担了完整闭环"],
    challenge:["难点与解法","Skill 建设的核心难点，是把隐性经验转成可执行约束"],
    growth:["成长与思考","从完成需求，到经营一套可复用的交付系统"]
  };
  head(slide,titles[kind][0],titles[kind][1],dark);
  if (kind==="summary") {
    tx(slide,"围绕三个 OKR，我把业务交付、工程治理和 AI 能力沉淀连成了一条完整的工作主线。",72,178,1050,32,{fontSize:20,color:C.gray});
    [["O1","业务交付质量","支撑内场调度与运营核心场景，生产 BUG 为 0，线上问题 24h 内闭环。",C.teal],["O2","前端基建与可观测性","统一核心技术栈并接入 Sentry，让问题更早暴露、定位更快。",C.blue],["O3","AI 赋能与个人效能","将 trunkFeeder-ui 的规则、约束和验证方法沉淀为项目级 skill，评测通过率提升 17pp。",C.orange]].forEach((r,i)=>{const y=250+i*116;box(slide,"roundRect",72,y,48,38,r[3]);tx(slide,r[0],72,y+7,48,24,{fontSize:14,bold:true,color:C.white,alignment:"center"});tx(slide,r[1],144,y-2,380,30,{fontSize:20,bold:true});tx(slide,r[2],144,y+34,930,44,{fontSize:16,color:C.gray});bar(slide,144,y+92,980,C.line,1)}); foot(slide,2); return;
  }
  if (kind==="o1") {
    tx(slide,"围绕内场调度、运营支撑和差异处理等核心链路持续交付，结果同时关注交付范围、线上稳定性和问题闭环速度。",72,178,790,54,{fontSize:20,color:C.gray}); bar(slide,72,268,720,C.line,2); tx(slide,"代表性工作",72,292,180,24,{fontSize:14,bold:true,color:C.teal});
    tx(slide,"内场调度：卸车看板、智能排班一期与二期\n运营支撑：人效、排班、食堂、周转箱等业务模块\n持续治理：字段口径、导出、报表性能与线上问题闭环",72,326,720,156,{fontSize:19}); box(slide,"roundRect",850,216,310,330,C.pale); metric(slide,"0","Q3 生产 BUG",890,260,C.teal); metric(slide,"24h","线上问题内解决",890,366,C.blue); metric(slide,"-20%","测试环节 BUG 率较上季度",890,472,C.orange); foot(slide,3); return;
  }
  if (kind==="timeline") {
    tx(slide,"同一条业务主线分两期推进，先建立可用能力，再补齐调度细节与效率反馈。",72,178,900,34,{fontSize:20,color:C.gray}); bar(slide,146,330,940,C.line,4); box(slide,"ellipse",210,306,50,50,C.teal); box(slide,"ellipse",698,306,50,50,C.orange); tx(slide,"1",210,316,50,24,{fontSize:18,bold:true,color:C.white,alignment:"center"}); tx(slide,"2",698,316,50,24,{fontSize:18,bold:true,color:C.white,alignment:"center"}); pill(slide,"一期：建立调度骨架",110,244,250,"#E4F4EE",C.teal); tx(slide,"路由与页面组织\n人员 / 车辆面板\n时间线任务条、月台调度看板",110,378,360,120,{fontSize:18}); pill(slide,"二期：补齐运营反馈",600,244,250,"#FFF0E4",C.orange); tx(slide,"任务绑定结束时间标记\n首发月台关系提示\n月台详情与操作效率指标",600,378,360,120,{fontSize:18}); tx(slide,"结果：调度任务、月台操作和效率反馈形成连续链路。",110,566,980,30,{fontSize:19,bold:true,color:C.teal}); foot(slide,4); return;
  }
  if (kind==="o2") {
    box(slide,"roundRect",72,196,500,300,C.pale); box(slide,"roundRect",616,196,500,300,"#EEF7F8"); tx(slide,"统一基础",108,230,180,24,{fontSize:14,bold:true,color:C.blue}); tx(slide,"React 17.0.2\nUmi 3.5.43\nAnt Design 4.24.14",108,270,300,120,{fontSize:25,bold:true}); tx(slide,"核心功能、构建与样式兼容性验证通过，减少环境差异带来的交付波动。",108,420,390,58,{fontSize:16,color:C.gray}); tx(slide,"问题可见",652,230,180,24,{fontSize:14,bold:true,color:C.teal}); tx(slide,"接入 Sentry\n测试环境先行\n生产环境落地",652,270,300,120,{fontSize:25,bold:true}); tx(slide,"让前端问题从“用户反馈后才知道”变成“运行中可观测、定位有入口”。",652,420,390,58,{fontSize:16,color:C.gray}); bar(slide,72,548,1044,C.line,2); tx(slide,"工程价值：把一次升级、一次接入，转化为多仓库可复用的交付底座。",72,574,1000,30,{fontSize:20,bold:true,color:C.teal}); foot(slide,5); return;
  }
  if (kind==="o3") {
    tx(slide,"这项 skill 是 Q3 绩效指标，也是我对个人效能提升的核心回答。",72,178,900,34,{fontSize:21,color:"#BFD2D9"}); tx(slide,"我把业务规则、设计系统、技术栈和验证清单整理成一套项目级上下文。",72,242,600,92,{fontSize:28,bold:true,color:C.white}); bar(slide,72,380,560,"#2B5361",2); tx(slide,"覆盖关键约束",72,408,200,24,{fontSize:14,bold:true,color:"#8FD0D0"}); tx(slide,"参数边界：centerCode / centerSiteCode\n业务枚举：网点与干线类型\n加载原则：慢接口不阻塞核心看板\n防幻觉：未发现的规范不允许补造",72,446,570,132,{fontSize:17,color:"#D6E5E9"}); box(slide,"roundRect",798,232,330,310,"#123D4E"); tx(slide,"对照评测",842,270,240,28,{fontSize:16,bold:true,color:"#8FD0D0",alignment:"center"}); metric(slide,"100%","有 Skill 的通过率",842,316,C.teal,true); metric(slide,"83%","无 Skill 的通过率",842,420,C.orange,true); tx(slide,"+17pp",1006,504,94,28,{fontSize:21,bold:true,color:"#F0B27A",alignment:"right"}); foot(slide,6,true); return;
  }
  if (kind==="roles") {
    tx(slide,"角色变化：从使用 AI 完成任务，转向设计 AI 如何稳定完成任务。",72,178,900,32,{fontSize:21,color:C.gray}); [["业务交付主力","内场调度、智能排班及运营支撑等核心模块的方案拆解、页面落地与问题闭环。",C.teal],["Skill 建设者","把 trunkFeeder-ui 的业务规则、设计系统和技术约束整理成可执行的项目上下文。",C.blue],["工程能力沉淀者","建立验证脚本、对照评测和交付清单，让经验能够被复用和检查。",C.orange]].forEach((r,i)=>{const x=72+i*358;bar(slide,x,282,260,r[2],6);tx(slide,r[0],x,316,280,36,{fontSize:22,bold:true});tx(slide,r[1],x,374,280,126,{fontSize:18,color:C.gray})});bar(slide,72,564,1044,C.line,2);tx(slide,"价值：让项目知识从个人记忆进入团队可复用的交付流程。",72,590,1000,30,{fontSize:20,bold:true,color:C.teal});foot(slide,7);return;
  }
  if (kind==="challenge") {
    [["问题",72,C.orange],["处理方式",376,C.teal],["留下的能力",824,C.blue]].forEach(r=>tx(slide,r[0],r[1],190,220,24,{fontSize:14,bold:true,color:r[2]}));
    [["业务规则分散在页面、接口与沟通中","抽取参数边界、枚举口径与示例","AI 修改代码时有清晰边界"],["多仓技术约束和组件用法不一致","把技术栈、组件用法和性能原则写进 Skill","减少跨仓返工与环境差异"],["AI 容易补造项目中不存在的规范","增加防幻觉约束与对照评测","从生成代码走向验证结果"]].forEach((r,i)=>{const y=238+i*112;bar(slide,72,y+78,1044,C.line,1);tx(slide,r[0],72,y,260,54,{fontSize:18});tx(slide,r[1],376,y,340,54,{fontSize:18,bold:true,color:C.teal});tx(slide,r[2],824,y,290,54,{fontSize:18,color:C.blue})});box(slide,"roundRect",72,594,1044,42,"#FFF0E4");tx(slide,"待完善：当前校验脚本仍查找旧目录名，需要改成仓库根目录相对路径。",92,604,1000,22,{fontSize:15,bold:true,color:C.orange});foot(slide,8);return;
  }
  if (kind==="growth") {
    box(slide,"roundRect",72,196,1044,104,C.navy);tx(slide,"我开始同时关注业务规则、工程边界和 AI 产出质量。",112,224,960,46,{fontSize:26,bold:true,color:C.white,alignment:"center"});bar(slide,72,350,1044,C.line,2);[["成长","能把复杂业务拆成规则、约束与验证项。",C.teal],["思考","修复和沉淀要落在正确的层，组件、机制和 Skill 才能产生复用。",C.blue],["下一步","持续贴近真实代码，补齐校验入口和场景评测，让 Skill 在更多页面稳定复用。",C.orange]].forEach((r,i)=>{const y=382+i*60;tx(slide,r[0],72,y,180,30,{fontSize:18,bold:true,color:r[2]});tx(slide,r[1],250,y,820,30,{fontSize:20})});foot(slide,9);return;
  }
}

async function writeBlob(file, value) { await fs.writeFile(file,new Uint8Array(await value.arrayBuffer())); }
async function main() {
  await fs.mkdir(buildDir,{recursive:true}); await fs.mkdir(renderDir,{recursive:true}); await fs.mkdir(path.dirname(final),{recursive:true});
  const deck=Presentation.create({slideSize:{width:1280,height:720}});
  data.forEach((item,index)=>{const slide=deck.slides.add();render(slide,item.kind,index+1);note(slide,item.notes);});
  for (const [i,slide] of deck.slides.items.entries()) await writeBlob(path.join(renderDir,"slide-"+String(i+1).padStart(2,"0")+".png"),await deck.export({slide,format:"png",scale:1.5}));
  await (await PresentationFile.exportPptx(deck)).save(draft);
  const {finalizePresentation}=await import("/Users/seminzhu/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/artifact_tool_utils.mjs");
  const result=await finalizePresentation({
    workspaceDir:root,candidatePath:draft,finalPath:final,
    pythonExecutable:"/Users/seminzhu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    integrityValidatorPath:"/Users/seminzhu/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/inspect_presentation_package_integrity.py",
    layoutValidatorPath:"/Users/seminzhu/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations/container_tools/inspect_presentation_layout_geometry.py",
    layoutArgs:["--expected-slide-size-emu","12192000,6858000","--validate-bullet-geometry","--validate-heading-fit"],
    requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
    fontPolicy:{basis:"design",families:[FONT]},verifyArtifactToolImport:true,
    receiptPath:path.join(buildDir,"2026-Q3-zhusemin-review.validation.json")
  });
  console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error);process.exitCode=1;});
