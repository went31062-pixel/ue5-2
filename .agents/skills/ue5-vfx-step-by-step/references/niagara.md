# 当前阶段：一个 Niagara 主发射器

基于 unreal-niagara 的层级、模块执行、参数驱动与验证流程改写。原文目标为 UE 5.8，本节以用户当前版本为准。

## 最小系统

创建或复制适合主效果的 System 和一个发射器。保留模板必要的生命周期模块，先用普通 CPU 发射器试做简单 Sprite；现有系统或大规模粒子应依据实际需求选择。不要自动改造已有 GPU 系统。

| 位置 | 负责的内容 |
| --- | --- |
| Emitter Update | 发射器生命周期，以及 Spawn Burst Instantaneous / Spawn Rate |
| Particle Spawn | Initialize Particle：初始寿命、尺寸、颜色等 |
| Particle Update | 粒子生命周期、每帧运动、颜色/尺寸曲线 |
| Render | Sprite / Mesh / Ribbon 等 Renderer 和材质/属性绑定 |

模块按阶段自上而下执行。初始化、力、速度求解以及后续覆盖必须与实际依赖顺序一致，保留模板的必要模块并根据编译诊断核对。不要把生成数量模块放在 Particle Update。

## 先能出现，再控制运动

第一轮：少量粒子、固定位置、固定尺寸、有效的材质引用，检查出生和结束。

第二轮只按需求加一个变化：速度、尺寸曲线或颜色/Alpha 曲线。动态力涉及 Solve Forces and Velocity 时，按模板和版本核对顺序；不同时修改多个阶段。

Sprite Renderer 核对材质及 Color Binding，常用粒子属性为 `Particles.Color`。最终 RGB/Alpha 是初始化、更新模块、Renderer 绑定和材质共同作用的结果；不要一律把 Spawn 和 Update 改成相同值。追踪后续模块是否覆盖或相乘，修改真正控制目标的那一步。

一次性效果核对系统/发射器的循环和结束条件。持续效果核对停止发射后已有粒子的行为。需要 GPU 时再确认 Bounds/Fixed Bounds、碰撞支持和目标平台限制；普通静止 Sprite 首轮无需增加这些配置。

## 参数与运行时触发

先用局部模块参数完成画面。用户需要从蓝图控制时，再建立合适的 User 参数并绑定到模块输入。完整记录参数名称和类型，例如 `User.FXColor`；调用工具/API 时按实际接口对名称的要求核对，不假设前缀总能省略。

只建立 User 参数而没有绑定到模块，不会自动改变效果。需要附着和跟随时确认 Local Space 与世界空间；快速移动物体的拖尾不能只靠多发几个原地 Sprite 解决，按需求选 Ribbon/Mesh 等方案。

## 看不见时的检查顺序

1. 时间是否走到出生段，生成数量与寿命是否非零，系统是否已激活。
2. Renderer 是否启用，材质是否指向正确资产，尺寸与 Alpha 是否有效。
3. 位置、相机、朝向与空间是否正确；出现视角消失时检查 Bounds/裁剪。
4. 查实际编译错误与模块顺序，不把所有问题都归结为亮度。

完成标准：Niagara 预览和实际关卡里都可见，主形状/运动可辨，一次性效果能结束，编译并保存成功。若只能指导用户操作，报告“等待 UE 画面验证”。

依据：[Epic 的 Niagara 概览](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine)、[Niagara Renderers](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-renderers)。
