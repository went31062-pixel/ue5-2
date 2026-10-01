# UE5.5 原生制作

适用已安装 UE5.5 的 Windows 环境。先读取 `Engine/Build/Build.version`，以实际 API 与资产路径为准；本仓库示例目标为 UE5.5.4。

## 贴图与材质

简单三角、圆环和几何符号可从矢量源精确导出 PNG，保留尺寸、线宽和顶点。噪声、烟、火等栅格素材按当前 imagegen skill 制作；不把 AI 生成视作通道、尺寸或平铺已经合格。

数据遮罩关闭 sRGB，并核对压缩设置和采样类型。需要透明背景时检查真实 Alpha；本示例的黑白 PNG 使用 R 通道，PNG 自身 Alpha 为全不透明，黑底的隐藏由材质实现。

通过 `AssetImportTask` 导入，通过 `MaterialEditingLibrary` 建立并连接节点、编译、创建实例。节点输入名称来自实际类／接口，连接函数返回值必须检查。UE5.5 的 `CustomInput` 用无参构造，再设置 `input_name`，不要假定可通过关键字构造。

单色发光图案可用 Unlit、Additive：遮罩 × 颜色 × 发光 × 显现进度送到 Emissive；黑色区域不增加画面颜色。Opacity 的乘法与材质混合方式一起核对，避免意外将淡出曲线乘两次。

## 一次发射的 Niagara

UE5.5 自带 `CascadeToNiagaraConverter` 提供 `FXConverterUtilitiesLibrary` 与 `NiagaraSystemConversionContext`，可以创建一个空发射器并通过转换上下文添加模块和 Renderer。这是编辑器工具，不是运行时依赖。

在独立工程启用 PythonScriptPlugin、EditorScriptingUtilities、Niagara 和 CascadeToNiagaraConverter。使用完整编辑器启动后执行 Python；纯 `-run=pythonscript` commandlet 没有完整 Slate 初始化，创建 Niagara System ViewModel 可能断言退出。

完整示例用 `UnrealEditor-Cmd.exe 工程.uproject -ExecutePythonScript=build_ue55.py`，保留正常 RHI。名称带 Cmd 不等于启用了 commandlet；这里不加 `-run=pythonscript`。`-NullRHI` 虽可保存部分资产，但本机保存场景时曾发生引擎除零异常，不能作为本示例的完整制作命令。

1. 创建 Niagara System，建立 SystemConversionContext，`add_empty_emitter`。
2. 按需求设置 CPU/GPU、Local Space；添加阶段正确的模块。
3. 使用类型正确的 ScriptInput 设置模块输入，检查 `set_parameter` 返回值。
4. 添加 Renderer 与材质；调用 System context `finalize` 提交图并请求编译。
5. 保存，结束创建上下文；在另一个编辑器进程重新加载并模拟，确认编译与实际行为。

`Initialize Particle` 的 Sprite Size 有模式开关：先设置 `ENiagara_SizeScaleMode` 的 `Non-Uniform`，再启用尺寸覆盖，不能只写二维尺寸。转换上下文在创建结束后清理，避免残留 ViewModel。

| 阶段 | 金色细三角示例 |
| --- | --- |
| Emitter Update | Emitter State：Self、Once、Complete；Spawn Burst：一个粒子、出生时间零 |
| Particle Spawn | Initialize Particle：寿命两秒、平面尺寸；设置 SpriteFacing 和 SpriteAlignment |
| Particle Update | Particle State：更新年龄、到寿命后结束 |
| Renderer | Sprite：自定义朝向，绑定金色材质实例 |

版本和枚举资产由引擎自带脚本与本地内容核对。仅找到方法名称并不足以确认模块参数；模块版本、静态开关和最后实际模拟结果都需要检查。

材质使用 `ParticleRelativeTime` 时，0 到 1 对应单个粒子的出生到寿命结束。示例寿命两秒，淡入区间 0–0.1，淡出区间 0.85–1；寿命改变时，这两段对应的实际秒数也会改变。

## 运行与录制

等待世界初始化和 Niagara 编译。调用 `ForceWaitForCompilationOnActivate` 可让本轮验证等待编译；不要在刚载入的同一瞬间把未激活误判为资产坏了。用 `NiagaraSimCacheFunctionLibrary.create_niagara_sim_cache` 先建立缓存，再记录、读回 Position、Age、Lifetime 和 SpriteSize。UE5.5 的立即捕获函数传入空缓存不会自动创建；系统完成后不可再捕获有效粒子帧，需要同时记录组件状态。

场景中的粒子可能已在编辑器预览里播放。测量一次全新触发时先 `reinitialize_system` 清理旧实例；只调用 `activate(reset=True)` 可能重置系统时间却留下上一轮粒子，造成计数重复。

真实短片使用引擎自带 Movie Render Queue，启用 MovieRenderPipeline。序列中的 Niagara 生命周期轨道使用 Desired Age、禁止中途重新激活，保证录制预热不会提前耗尽效果。异步 Python 保持脚本存活，在录制完成回调里退出编辑器。示例 `render_preview.py` 输出原生 PNG 帧，再编码 MP4；不把网页重画当作 UE 渲染。

启动后立即在 PIE 中录制可能早于世界首次有效 Tick，导致开头使用默认 FOV、粒子未模拟。示例设置 `MoviePipelinePIEExecutorSettings.initial_delay_frame_count=60`，先让 PIE 初始化，再录制；不要把缺少开头的短片当成已经验证显现过程。

## 必要模型

平面符号使用 Sprite；需要弯曲轮廓、厚度或真实空间体积时再制作 Mesh。模型记录厘米尺度、UV、枢轴和材质槽，在 UE 内导入后核对。不要为了凑齐“模型”交付制造无用几何。

## 技术依据

- [UE5.5 MaterialEditingLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialEditingLibrary?application_version=5.5)
- [UE5.5 FXConverterUtilitiesLibrary](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FXConverterUtilitiesLibrary?application_version=5.5)
- 本机 UE5.5 `CascadeToNiagaraConverter/Content/Python` 的模块路径、阶段和输入示例；不随仓库复制引擎实现代码。
