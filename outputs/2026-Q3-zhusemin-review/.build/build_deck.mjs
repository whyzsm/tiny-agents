import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const root = "/Users/seminzhu/Documents/AI/tiny-agents/outputs/2026-Q3-zhusemin-review";
const buildDir = path.join(root, ".build");
const renderDir = path.join(root, "rendered");
const draft = path.join(buildDir, "draft.pptx");
const final = path.join(root, "deliverables", "2026-Q3-zhusemin-review.pptx");
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
  {kind:"cover",notes:"开场：先给结论，再按 O1、O2、O3 展开。Q3 不只完成业务需求，也把项目经验沉淀成可复用的 AI 工程化能力。来源：用户提供的 2026 Q3 OKR 截图与 2026-06-01 至 2026-10-13 工作报告。"},
  {kind:"summary",notes:"只讲三条主线，不展开仓库清单。O3 的 trunkFeeder-ui/skill 是绩效指标本身，应明确说成独立成果。来源：Q3 OKR 截图、工作报告、trunkFeeder-ui/skill 仓库审阅。"},
  {kind:"o1",notes:"截图中的完成成果描述给出生产 BUG 为 0、线上问题 24h 内解决、测试环节 BUG 率较上季度下降 20%。来源：Q3 O1 OKR 截图；工作报告补充代表性业务范围。"},
  {kind:"timeline",notes:"用这个案例说明你参与了业务链路拆解和逐期交付，不只是页面开发。来源：工作报告中 trunkFeeder-ui 的智能排班一期、二期内容。"},
  {kind:"o2",notes:"不讲依赖升级细节，而讲统一技术栈和可观测性如何服务交付质量。截图给出 React、Umi、Ant Design 版本和构建、样式兼容性目标；工作报告补充 Sentry 接入和依赖治理。来源：Q3 O2 OKR 截图、工作报告。"},
  {kind:"o3",notes:"明确绑定绩效：trunkFeeder-ui/skill 是 O3 的关键举措，不是横向工作附录。初版 6/30，重构版 8/3，包含 SKILL.md、business-rules、design-system、tech-stack 和验证脚本。评测报告给出 with_skill 100% ±0、without_skill 83% ±14，差值 +17pp。来源：Q3 O3 OKR 截图；skill 文件与提交记录 2ba7bff、bcf923a、eec41a7、cc038ab。"},
  {kind:"roles",notes:"回答项目角色：业务规则抽取、工程约束设计、评测验证和交付整理。来源：skill/SKILL.md、references/*.md、评测提交记录。"},
  {kind:"challenge",notes:"真实验证边界：直接运行当前 skill/scripts/validate-project-skill.sh 会因脚本仍查找旧的 T-MAX 根目录和 trank-feeder-main 路径而失败。这不等于 skill 内容无效，但说明校验脚本需要跟随目录重构同步更新。来源：2026-10-13 对 trunkFeeder-ui 的现场审阅与脚本运行结果。"},
  {kind:"growth",notes:"成长落到行为变化：以后面对类似项目，不只写功能，也会主动识别业务规则、质量边界和 AI 可复用资产。下一步是建议，不作为 Q3 已完成事实。来源：Q3 O3 目标描述、skill 仓库现状和验证结果。"},
  {kind:"closing",notes:"结束语：停在三句话即可。若现场追问，再补充各仓库需求清单和 skill 文件结构。来源：本次述职材料综合 Q3 OKR 截图、T-MAX 工作报告、trunkFeeder-ui/skill 仓库审阅。"}
];

function render(slide, kind, page) {
  if (kind==="cover") {
    slide.background.fill=C.navy; bar(slide,72,94,104,C.orange,5);
    tx(slide,"2026 Q3",72,140,400,42,{fontSize:23,bold:true,color:"#BFD2D9"});
    tx(slide,"述职汇报",72,194,650,100,{fontSize:56,bold:true,color:C.white});
    tx(slide,"业务交付与 AI 工程化并进",76,314,600,42,{fontSize:24,color:"#BFD2D9"});
    tx(slide,"朱色敏  ·  00118740",76,590,420,28,{fontSize:16,color:"#BFD2D9"});
    tx(slide,"前端研发 / T-MAX",76,624,360,24,{fontSize:14,color:"#8FAAB4"});
    tx(slide,"Q3",866,190,300,190,{fontSize:164,bold:true,color:"#17475A",alignment:"center"});
    bar(slide,900,408,232,C.teal,5); tx(slide,"交付 · 稳定 · 复用",862,438,310,30,{fontSize:15,bold:true,color:"#BFD2D9",alignment:"center"}); foot(slide,page,true); return;
  }
  if (kind==="closing") {
    slide.background.fill=C.navy; bar(slide,72,154,110,C.orange,5); tx(slide,"Q3 总结",72,202,300,34,{fontSize:18,bold:true,color:"#BFD2D9"});
    tx(slide,"把交付经验\n变成可复用能力",72,258,760,150,{fontSize:54,bold:true,color:C.white});
    tx(slide,"业务交付有结果，工程建设有沉淀，AI 使用有方法。",76,464,720,38,{fontSize:24,color:"#BFD2D9"}); tx(slide,"谢谢",956,538,190,42,{fontSize:30,bold:true,color:"#8FD0D0",alignment:"right"}); foot(slide,page,true); return;
  }
  slide.background.fill = kind==="summary"||kind==="timeline"||kind==="roles"||kind==="growth" ? C.pale : C.white;
  if (kind==="o3") slide.background.fill=C.navy;
  const dark = kind==="o3";
  const titles={
    summary:["核心结论","Q3 的主线，是把一次次交付变成稳定、可复用的交付能力"],
    o1:["O1 业务交付","业务交付从“按时完成”进一步落到“上线后稳定运行”"],
    timeline:["重点案例","智能排班把复杂调度规则推进到可运营的功能闭环"],
    o2:["O2 前端基建","统一技术栈与可观测性，降低多仓库协作的维护成本"],
    o3:["O3 AI 赋能","trunkFeeder-ui/skill：把项目经验变成 AI 可执行的工程资产"],
    roles:["项目角色","我在 skill 项目中承担了从提炼到验证的完整闭环"],
    challenge:["难点与解法","真正的难点，不是写文档，而是把隐性经验变成可执行约束"],
    growth:["成长与思考","我开始关注的不只是“这次做成了什么”，还有“下次能否更快做对”"]
  };
  head(slide,titles[kind][0],titles[kind][1],dark);
  if (kind==="summary") {
    tx(slide,"围绕三个 OKR，我完成了从业务交付到工程治理，再到 AI 能力沉淀的连续推进。",72,178,1050,32,{fontSize:20,color:C.gray});
    [["O1","业务交付质量","支撑内场调度与运营核心场景，生产 BUG 为 0，线上问题 24h 内闭环。",C.teal],["O2","前端基建与可观测性","统一核心技术栈并接入 Sentry，让问题更早暴露、定位更快。",C.blue],["O3","AI 赋能与个人效能","将 trunkFeeder-ui 的规则、约束和验证方法沉淀为项目级 skill，评测通过率提升 17pp。",C.orange]].forEach((r,i)=>{const y=250+i*116;box(slide,"roundRect",72,y,48,38,r[3]);tx(slide,r[0],72,y+7,48,24,{fontSize:14,bold:true,color:C.white,alignment:"center"});tx(slide,r[1],144,y-2,380,30,{fontSize:20,bold:true});tx(slide,r[2],144,y+34,930,44,{fontSize:16,color:C.gray});bar(slide,144,y+92,980,C.line,1)}); foot(slide,2); return;
  }
  if (kind==="o1") {
    tx(slide,"围绕内场调度、运营支撑和差异处理等核心链路持续交付，结果指标聚焦质量与闭环速度。",72,178,760,54,{fontSize:20,color:C.gray}); bar(slide,72,268,720,C.line,2); tx(slide,"代表性工作",72,292,180,24,{fontSize:14,bold:true,color:C.teal});
    tx(slide,"内场调度：卸车看板、智能排班一期与二期\n运营支撑：人效、排班、食堂、周转箱等业务模块\n持续治理：字段口径、导出、报表性能与线上问题闭环",72,326,720,156,{fontSize:19}); box(slide,"roundRect",850,216,310,330,C.pale); metric(slide,"0","Q3 生产 BUG",890,260,C.teal); metric(slide,"24h","线上问题内解决",890,366,C.blue); metric(slide,"-20%","测试环节 BUG 率较上季度",890,472,C.orange); foot(slide,3); return;
  }
  if (kind==="timeline") {
    tx(slide,"同一条业务主线分两期推进，先建立可用能力，再补齐调度细节与效率反馈。",72,178,900,34,{fontSize:20,color:C.gray}); bar(slide,146,330,940,C.line,4); box(slide,"ellipse",210,306,50,50,C.teal); box(slide,"ellipse",698,306,50,50,C.orange); tx(slide,"1",210,316,50,24,{fontSize:18,bold:true,color:C.white,alignment:"center"}); tx(slide,"2",698,316,50,24,{fontSize:18,bold:true,color:C.white,alignment:"center"}); pill(slide,"一期：建立调度骨架",110,244,250,"#E4F4EE",C.teal); tx(slide,"路由与页面组织\n人员 / 车辆面板\n时间线任务条、月台调度看板",110,378,360,120,{fontSize:18}); pill(slide,"二期：补齐运营反馈",600,244,250,"#FFF0E4",C.orange); tx(slide,"任务绑定结束时间标记\n首发月台关系提示\n月台详情与操作效率指标",600,378,360,120,{fontSize:18}); tx(slide,"结果：从单页面开发，推进到“调度任务 → 月台操作 → 效率反馈”的连续链路。",110,566,980,30,{fontSize:19,bold:true,color:C.teal}); foot(slide,4); return;
  }
  if (kind==="o2") {
    box(slide,"roundRect",72,196,500,300,C.pale); box(slide,"roundRect",616,196,500,300,"#EEF7F8"); tx(slide,"统一基础",108,230,180,24,{fontSize:14,bold:true,color:C.blue}); tx(slide,"React 17.0.2\nUmi 3.5.43\nAnt Design 4.24.14",108,270,300,120,{fontSize:25,bold:true}); tx(slide,"核心功能、构建与样式兼容性验证通过，减少环境差异带来的交付波动。",108,420,390,58,{fontSize:16,color:C.gray}); tx(slide,"问题可见",652,230,180,24,{fontSize:14,bold:true,color:C.teal}); tx(slide,"接入 Sentry\n测试环境先行\n生产环境落地",652,270,300,120,{fontSize:25,bold:true}); tx(slide,"让前端问题从“用户反馈后才知道”变成“运行中可观测、定位有入口”。",652,420,390,58,{fontSize:16,color:C.gray}); bar(slide,72,548,1044,C.line,2); tx(slide,"工程价值：把一次升级、一次接入，转化为多仓库可复用的交付底座。",72,574,1000,30,{fontSize:20,bold:true,color:C.teal}); foot(slide,5); return;
  }
  if (kind==="o3") {
    tx(slide,"这项 skill 是 Q3 绩效指标，也是我对个人效能提升的核心回答。",72,178,900,34,{fontSize:21,color:"#BFD2D9"}); tx(slide,"我沉淀的不是一段提示词，而是一套项目级上下文：业务规则、设计系统、技术栈、验证清单。",72,242,600,92,{fontSize:28,bold:true,color:C.white}); bar(slide,72,380,560,"#2B5361",2); tx(slide,"覆盖关键约束",72,408,200,24,{fontSize:14,bold:true,color:"#8FD0D0"}); tx(slide,"参数边界：centerCode / centerSiteCode\n业务枚举：网点与干线类型\n加载原则：慢接口不阻塞核心看板\n防幻觉：未发现的规范不允许补造",72,446,570,132,{fontSize:17,color:"#D6E5E9"}); box(slide,"roundRect",798,232,330,310,"#123D4E"); tx(slide,"评测结果",842,270,240,28,{fontSize:16,bold:true,color:"#8FD0D0",alignment:"center"}); metric(slide,"100%","有 Skill 的通过率",842,316,C.teal,true); metric(slide,"83%","无 Skill 的通过率",842,420,C.orange,true); tx(slide,"+17pp",1006,504,94,28,{fontSize:21,bold:true,color:"#F0B27A",alignment:"right"}); foot(slide,6,true); return;
  }
  if (kind==="roles") {
    tx(slide,"角色变化：从使用 AI 完成任务，转向设计 AI 如何稳定完成任务。",72,178,900,32,{fontSize:21,color:C.gray}); [["业务规则提炼","从页面、接口和实际场景中抽取规则，明确哪些约束必须被 AI 继承。",C.teal],["工程约束设计","把设计系统、技术栈、性能加载原则和防幻觉边界写成可检索的参考资料。",C.blue],["效果评测与交付","建立 with / without skill 对照评测，并保留验证脚本和交付清单。",C.orange]].forEach((r,i)=>{const x=72+i*358;bar(slide,x,282,260,r[2],6);tx(slide,r[0],x,316,280,36,{fontSize:22,bold:true});tx(slide,r[1],x,374,280,126,{fontSize:18,color:C.gray})});bar(slide,72,564,1044,C.line,2);tx(slide,"价值：让项目知识从“个人记忆”进入“团队可复用的交付流程”。",72,590,1000,30,{fontSize:20,bold:true,color:C.teal});foot(slide,7);return;
  }
  if (kind==="challenge") {
    [["问题",72,C.orange],["处理方式",376,C.teal],["留下的能力",824,C.blue]].forEach(r=>tx(slide,r[0],r[1],190,220,24,{fontSize:14,bold:true,color:r[2]}));
    [["业务规则分散在页面、接口与沟通中","抽取参数边界与枚举口径","AI 修改代码时有明确边界"],["慢接口容易拖住核心看板首屏","把首屏优先级写进性能规则","交付时默认关注用户可用性"],["AI 容易补造项目中不存在的规范","增加防幻觉约束与评测","从“生成得像”转向“符合项目”"]].forEach((r,i)=>{const y=238+i*112;bar(slide,72,y+78,1044,C.line,1);tx(slide,r[0],72,y,260,54,{fontSize:18});tx(slide,r[1],376,y,340,54,{fontSize:18,bold:true,color:C.teal});tx(slide,r[2],824,y,290,54,{fontSize:18,color:C.blue})});box(slide,"roundRect",72,594,1044,42,"#FFF0E4");tx(slide,"验证边界：当前仓库内校验脚本仍按旧目录命名查找，后续需修正为仓库根目录相对路径。",92,604,1000,22,{fontSize:15,bold:true,color:C.orange});foot(slide,8);return;
  }
  if (kind==="growth") {
    box(slide,"roundRect",72,196,1044,104,C.navy);tx(slide,"从页面交付，到业务建模、工程治理和 AI 工作流设计，研发视角开始向交付系统扩展。",112,224,960,46,{fontSize:26,bold:true,color:C.white,alignment:"center"});bar(slide,72,350,1044,C.line,2);[["成长","能把复杂业务拆成规则、约束与验证项。",C.teal],["思考","skill 的长期价值不在于写得多，而在于持续贴近真实代码、持续被评测。",C.blue],["下一步","修正校验入口，扩充场景评测，把高频规则继续沉淀为组件与 hooks。",C.orange]].forEach((r,i)=>{const y=382+i*60;tx(slide,r[0],72,y,180,30,{fontSize:18,bold:true,color:r[2]});tx(slide,r[1],250,y,820,30,{fontSize:20})});foot(slide,9);return;
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
