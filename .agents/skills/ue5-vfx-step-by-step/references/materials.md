# 当前阶段：基础材质

基于 shader-programming 的 UV、纹理采样、颜色乘法和效果控制概念改写，使用 UE 材质节点表达，不直接粘贴 GLSL。

## 选择最小结构

先确认项目使用的材质体系。本节连线是传统 Surface 材质的入门示例；Substrate 或项目专用主材质须按实际体系核对，不能强行套相同端口。

发光能量可先试 Unlit + Additive；需要保留灰暗形状的烟雾可先试 Unlit + Translucent。二者都需根据背景、深度和曝光观察。Additive 叠加会提亮，不能靠黑色遮住背景。

第一轮只做“形状 × 颜色”和透明度。示例：
- TextureSampleParameter2D（贴图参数）读取 `T_Main`；UV 先用默认坐标。
- 灰度形状取 R 通道；真实透明彩色图取 Alpha。将结果记作 `Mask`。
- VectorParameter（颜色参数）`Tint` 默认白色。
- ScalarParameter（亮度参数）`Intensity` 默认 1。
- `Tint.RGB × ParticleColor.RGB × Intensity` 接 Emissive Color。
- `Saturate(Mask × ParticleColor.A)` 接 Opacity。

这是未预乘颜色的 Additive/Translucent 起点，遮罩只通过 Opacity 参与混合。不要无意在 Emissive 和 Opacity 中重复相乘造成遮罩平方；如果素材已经预乘或使用 AlphaComposite，须重新核对合成方式。彩色纹理时可额外乘其 RGB，但先明确其是否已预乘。

若当前使用程序形状，把其输出作为 Mask；不凭空引用不存在的纹理。粒子颜色节点（Particle Color）负责接收粒子颜色/透明度；实际效果仍需在 Niagara Renderer 和粒子属性中核对。

## 分两次验证

1. 编译材质，查看遮罩和颜色能否表达形状。材质预览无法充分验证粒子属性绑定；必要时临时用白色常量和 Alpha=1 隔离问题。
2. 在一个测试粒子上验证 Particle Color 的 RGB/Alpha。设置供对应 Renderer 使用的材质 Usage；确认无编译错误后保存。按项目习惯使用材质实例调参数。

完成标准：主形状正确，透明区正确，颜色/亮度可调，粒子 Alpha=0 时确实消失。暂不以固定亮度数值保证最终观感。

## 后续只添加本轮需要的一项

- 流动：Panner 改采样 UV，确认平铺方式和运动方向。
- 消融：噪声与阈值比较；软透明过渡和硬裁切走不同输出。不要把 Masked 的 Opacity Mask 接法套到 Translucent。
- 贴地边缘：确实发生深度交界硬边时再检查 Depth Fade。
- 扭曲：确认空间、采样和版本支持后添加，不同时改透明度曲线。
- 泛白：先比较曝光、Bloom、亮度和叠加数量。不要把亮度盲目拉高。

依据：[Epic 的材质混合模式](https://dev.epicgames.com/documentation/en-us/unreal-engine/material-blend-modes-in-unreal-engine)、[粒子材质表达式](https://dev.epicgames.com/documentation/en-us/unreal-engine/particle-expressions)。节点名称和可用端口以用户版本为准。
