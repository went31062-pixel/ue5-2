# 来源与取舍

检索日期：2026-10-01。通过 GitHub 插件检索并读取原始文件，再参照 Epic 文档组合为中文 UE5 特效流程。

## 采用的三个来源

上游：[gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills)，固定 commit：`d4b0e35550c55ae70bdfcab4ef5a0e94610438a9`。

| 原始路径 | 本地原文快照 | 组合方式 |
| --- | --- | --- |
| [skills/unreal/unreal-niagara/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/unreal/unreal-niagara/SKILL.md) | [unreal-niagara.md](third_party/gamedev-skills/unreal-niagara.md) | 改写为一个主发射器、阶段/顺序、参数绑定和画面验证 |
| [skills/disciplines/shader-programming/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/shader-programming/SKILL.md) | [shader-programming.md](third_party/gamedev-skills/shader-programming.md) | 将跨引擎概念改写成 UE 材质节点思路，去掉其他引擎语法 |
| [skills/disciplines/create-game-assets/SKILL.md](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/SKILL.md) | [create-game-assets.md](third_party/gamedev-skills/create-game-assets.md) | 收敛为当前特效所需的少量贴图、通道与导入验证 |

原文文件内容保持不变，仅将文件名改为普通 Markdown，作为来源档案而非可安装 skill。原文中的其他 skill、脚本、assets 和 references 没有一并导入，不应从快照直接执行流程；需要完整上游时访问上述固定版本。可用组合版的支持文件全部随仓库提供。

上游 Apache-2.0 的完整 [LICENSE](third_party/gamedev-skills/LICENSE) 和 [NOTICE](third_party/gamedev-skills/NOTICE) 随附，适用于这些原文快照和基于它们的阶段参考改写。原文著作权归上游作者和贡献者。本仓库的中文入口、示例和阶段参考为针对本次需求的整合修改，不代表上游官方发布或 Epic 背书。

原始文件的路径、版本及 Git blob SHA 记录在 [sources.lock.json](sources.lock.json)。发布前将本地快照与上游 Git blob SHA 对比，避免误截断。

## 已查看但未加入默认流程

- [EpicGames/unreal-engine-skills-for-claude-code-plugin 的 unreal-mcp](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin/blob/a6aa73ada02a9fb1f5415bec491f9942c519b297/skills/unreal-mcp/SKILL.md)：用于已有实时 UE 编辑器 MCP 连接的工具发现和操作。当前任务是组合 skill，没有可验证的 UE 连接，先保留来源；未来需要直接操作编辑器时再检查当前项目的引擎版本和连接条件。
- [VibeUE 的 niagara-emitters](https://github.com/kevinpbuckley/VibeUE/blob/a231dcb57f22958ccb5207d9588dd357f2921f0d/Content/Skills/niagara-emitters/SKILL.md)：依赖 VibeUE 服务及引擎工具集，侧重颜色曲线、参数和 Scratch Pad。首轮制作不需要这些依赖，未复制或安装。

## 兼容性与纠正

原始 Niagara skill 明确写着目标 UE 5.8，不等于用户工程是该版本或所有版本已测试。组合版要求先确定实际版本，再核对该版本模块、材质体系和工具 schema。

组合时没有照搬“所有参数都必须同时改 Spawn/Update”“User 名称前缀可以固定省略”或“生成 PNG 就有透明度”等未经项目验证的假设。参数按实际数据流、接口与通道确认。也没有把通用 GLSL 片段直接当成 UE 材质节点。

## 官方技术依据

阶段参考只归纳本次需要的概念，不复制整本教程：
- [Niagara Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine)：层级、执行阶段和模块顺序。
- [Material Blend Modes](https://dev.epicgames.com/documentation/en-us/unreal-engine/material-blend-modes-in-unreal-engine)：混合方式及背景表现。
- [Using Texture Masks](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-texture-masks-in-unreal-engine)：数据遮罩通道和 sRGB。
- [Particle Expressions](https://dev.epicgames.com/documentation/en-us/unreal-engine/particle-expressions) 与 [Niagara Renderers](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-renderers)：运行时应在用户对应版本继续核对的绑定参考；本次检索未完整取得这两页正文。

以上是前期 skill 组合时的验证范围。当时仅验证仓库和文本；后续实际制作的验证见下方“UE5.5 单层制作”。

## 本次增加：单层理解与简单中文

用户进一步要求：每次只理解一层的贴图、材质、粒子和作用，用短表格、彩色/去色图卡辅助，提供修改与用途方向；不默认完成整套效果。

在本次读到的候选中，没有发现完整覆盖这一组要求的流程。这个结论限于本次检索，不代表 GitHub 上不存在相关项目。单层分析、证据标签、图卡、修改和迁移流程是本仓库针对需求创作的内容。

| 查看过的来源 | 适合什么 | 本次取舍 |
| --- | --- | --- |
| [obra/the-elements-of-style 的 writing-clearly-and-concisely](https://github.com/obra/the-elements-of-style/blob/05fc4f0d2b97b7c042dd9949ad658568e4a1324e/skills/writing-clearly-and-concisely/SKILL.md) | 主动表达、具体用词、删除多余内容 | 将一般表达原则独立改写为中文，未复制原文或整本参考书 |
| [claude-dev-suite 的 vfx-2d](https://github.com/claude-dev-suite/claude-dev-suite/blob/aa861d9a7eb12fd3d18a78358abf5ca07c3ab88f/skills/gamedev/2d-art/vfx-2d/SKILL.md) | 烟火水电等 2D 效果、分帧和叠加 | 不是 UE 单层参考分析流程，未导入，也未照搬其帧数 |
| [agency-agents 的 Unreal Technical Artist](https://github.com/msitarzewski/agency-agents/blob/e31d699e06e78056489bb72282b754dfaa4b254a/game-development/unreal-engine/unreal-technical-artist.md) | UE 材质、Niagara、PCG 和性能制作 | 范围较大、术语较多；未导入或采用固定粒子数/性能阈值 |

表达来源 README 标注 1918 书籍文本为 Public Domain，但这不能自动证明现代包装文件都采用相同许可证；本次只记录参考链接和文件版本，不复制现代包装文件。中文表达 skill 是独立创作的一般写作指导。

检索词包括 `VFX breakdown SKILL.md`、`vfx SKILL.md niagara`、`niagara reference analysis layers`、`writing-clearly-and-concisely`、`plain language SKILL.md` 和中文简洁表达相关词。完整流程缺口没有用一堆通用 skill 填充。

新增脚本仅将既有图片嵌入离线 HTML；彩色与去色预览共用同一源图，不改变像素，不自动抽取真实图层。默认图卡是原创圆环示意，不是 UE 渲染或游戏截图。

新增验证范围：两个 skill 的结构、支持文件引用、图卡包装和浏览器显示/交互；没有把推测视作原作者资产，也没有宣称 UE 画面已验证。

## 本次增加：UE5.5 单层制作

用户要求从观察、原理继续到实际贴图、材质、粒子和 UE 预览。在已查看的候选中，没有找到同时覆盖 UE5.5、少量逐层制作、简明中文、保存重开与实际预览确认的完整流程，因此新建 [ue55-vfx-layer-production](.agents/skills/ue55-vfx-layer-production/SKILL.md)。这是本仓库原创流程，不额外堆叠通用 skill。

继续核对了前述 Epic MCP 与 VibeUE 路线：使用它们之前须验证工具连接、目标引擎版本和依赖；当前 UE5.5 工程不假定具备新的引擎工具集，也没有复制或安装候选项目。本轮采用 UE5.5 自带的编辑器 Python、材质编辑库、CascadeToNiagaraConverter 转换上下文与 Movie Render Queue。

| 技术依据 | 用在哪里 |
| --- | --- |
| [UE5.5 MaterialEditingLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialEditingLibrary?application_version=5.5) | 创建连线、编译材质、设置实例 |
| [UE5.5 FXConverterUtilitiesLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FXConverterUtilitiesLibrary?application_version=5.5) | 原生 Niagara 转换上下文与类型正确的输入 |
| 本机 UE5.5.4 `CascadeToNiagaraConverter/Content/Python` | 核对模块路径、版本、枚举与尺寸开关；未复制引擎代码到仓库 |
| 本机 UE5.5.4 Niagara / MovieRenderPipeline API 与源码 | 核对生命周期轨道、缓存读取和异步录制回调；按实际运行结果修正 |

新增验证范围：金色细三角原生资产在 **UE5.5.4-40574608** 创建、编译、保存、新进程重开、CPU 粒子缓存读取，以及 Movie Render Queue 实际 PNG 帧与 MP4。其余结构示例与第三方 skill 不因这个测试自动获得兼容性证明。失败的纯 commandlet、NullRHI 场景保存和旧录制路径保留在本地排错记录，不作为成功验证。

源贴图是原创矢量几何导出，UE 资产与短片是本轮自行制作；不包含用户参考视频或原作者原始资产。颜色和淡出节奏明确标为试做，隐藏的原始制作方法仍是推测。
