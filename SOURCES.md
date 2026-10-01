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

本次仅验证仓库和 skill 文本；没有宣称实际 UE 画面、所有 API 或工具连接已验证。
