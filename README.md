# UE5 特效：用 AI 一步步做

把“描述需求 → 贴图/材质 → Niagara → 看画面调整”组合成一个中文 Codex skill。只启用一个入口，需要哪一步才读取对应参考。

## 开始使用

在 Codex 中打开这个仓库，输入：

> 使用 $ue5-vfx-step-by-step 帮我做一个蓝色命中特效。我用 UE 5.x，先完成主效果，每次只给当前阶段的少量步骤，做完根据画面继续。

把 `5.x` 换成自己的版本；有参考图、录屏、已有资产时一起提供。已有材质或 Niagara 系统可以从当前进度接着做。

| 顺序 | 当前目标 | 本步完成的标志 |
| --- | --- | --- |
| 1 | 把效果说清楚 | 主形状、颜色、运动和时长能描述出来 |
| 2 | 做必要的贴图和基础材质 | 主形状、颜色和透明度正确 |
| 3 | 创建一个 Niagara 主发射器 | 能播放一次，运动和消失正常 |
| 4 | 对照画面逐轮调整 | 每轮解决一个差异，再决定是否加细节 |

不要先读完所有文件。入口是 [.agents/skills/ue5-vfx-step-by-step/SKILL.md](.agents/skills/ue5-vfx-step-by-step/SKILL.md)，第一练习见 [examples/first-effect.md](examples/first-effect.md)。

## 找到并组合的 skill

| GitHub 来源 | 采用的部分 | 放在哪里 |
| --- | --- | --- |
| [unreal-niagara](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/unreal/unreal-niagara/SKILL.md) | 系统/发射器/模块、执行阶段、参数和验证 | Niagara 阶段参考 |
| [shader-programming](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/shader-programming/SKILL.md) | UV、遮罩、颜色、消融和坐标空间 | 材质阶段参考 |
| [create-game-assets](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/d4b0e35550c55ae70bdfcab4ef5a0e94610438a9/skills/disciplines/create-game-assets/SKILL.md) | 先确定用途、少量制作、检查透明度和导入结果 | 贴图阶段参考 |

组合版经过中文重写和 UE5 特效范围收敛；原始文本快照、固定版本及许可证在 [SOURCES.md](SOURCES.md) 和 [third_party/gamedev-skills](third_party/gamedev-skills)。原文快照用于追溯，不作为额外安装的 skill。

## 能力与验证范围

这是给 AI 的工作方法，仓库本身没有 UE 编辑器连接、生成模型或可运行的 `.uasset`。普通聊天可以提供节点连线、参数和排错步骤；实际生成图片需要可用的图像工具，直接修改 UE 需要已连接且支持相应操作的编辑器工具。

原始 Niagara skill 标注目标 UE 5.8。组合版每次先确认实际版本，按当前编辑器和该版本官方文档核对节点/模块；没有在你的 UE 项目里做兼容性测试。

当前只检查 skill 格式、文件链接、来源快照完整性和 GitHub 发布结果。画面效果须在 UE 中验证。

检索与整理日期：2026-10-01。第三方快照及参考改写遵循 Apache-2.0，见随附 LICENSE 与 NOTICE。
