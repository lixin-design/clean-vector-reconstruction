<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md"><strong>简体中文</strong></a>
</p>

# Clean Vector Reconstruction

把位图插画重建成干净、可编辑的 SVG，放进 Adobe Illustrator 里接着改。

Clean Vector Reconstruction 是一个面向 AI Agent 的 Skill，适合处理扁平、半扁平和几何色块插画。它会根据参考图分析构图、拆分对象，再用矢量图形重新搭出画面。

重建时会同时考虑画面还原和后续编辑。主要物体可以单独选中，色块和渐变能继续调整，路径也尽量保持简洁，方便你接手修改。

## 适合什么样的图

色块边界清楚、物体结构明确的插画，都很适合从这里开始。比如几何插画、静物，或由建筑、家具和货架组成的场景。

画面里的东西多一些也没关系。只要能看清各个物体的形状和前后关系，就可以逐步拆开重建。重复元素还可以统一处理尺寸和排列关系。

照片、厚重笔触和密集纹理超出了这套 Skill 的主要适用范围。手指、头发、复杂动物姿态等依赖细微轮廓的内容，也通常需要更多手工调整。

## 重建后的效果

下面五组示例展示了参考图和重建结果。

### Geometric Harvest · 几何色块

| 参考图 | 重建 SVG |
| --- | --- |
| ![Geometric Harvest 参考图](examples/geometric-harvest/reference.png) | [![Geometric Harvest 重建图](examples/geometric-harvest/preview.png)](examples/geometric-harvest/reconstruction-layered.svg) |

大面积色块配合少量渐变，适合用简洁的几何图形重建。

### Still Life · 静物

| 参考图 | 重建 SVG |
| --- | --- |
| ![Still Life 参考图](examples/still-life/reference.png) | [![Still Life 重建图](examples/still-life/preview.png)](examples/still-life/reconstruction-layered.svg) |

水果、器皿、叶子和桌面分别作为对象处理。水果和叶片的曲线保留各自的形状，方便后续单独调整。

### Winter Street · 冬日街景

| 参考图 | 重建 SVG |
| --- | --- |
| ![Winter Street 参考图](examples/winter-street/reference.png) | [![Winter Street 重建图](examples/winter-street/preview.png)](examples/winter-street/reconstruction-layered.svg) |

先确定建筑和道路的位置，再处理灯光与积雪。元素虽然多，仍然可以按场景结构组织成清楚的分组。

### Kitchen Interior · 厨房

| 参考图 | 重建 SVG |
| --- | --- |
| ![Kitchen Interior 参考图](examples/kitchen-interior/reference.png) | [![Kitchen Interior 重建图](examples/kitchen-interior/preview.png)](examples/kitchen-interior/reconstruction-layered.svg) |

重复出现的柜门和器皿，可以一起处理比例与间距。

### Market Shelf · 货架

| 参考图 | 重建 SVG |
| --- | --- |
| ![Market Shelf 参考图](examples/market-shelf/reference.png) | [![Market Shelf 重建图](examples/market-shelf/preview.png)](examples/market-shelf/reconstruction-layered.svg) |

先搭好货架，再组织每层的商品、容器和木箱。重复物件沿用共同的构造，同时保留参考图里的局部差异。

## 它是怎么做的

先看整体，再画对象，最后补细节。

重建从画布比例和大色块开始，先确定主要物体的位置、间距与遮挡关系。构图确定后，再逐个处理物体轮廓，补上渐变、描边和局部细节。

规则形状优先使用矩形、圆和椭圆等 SVG 原生图形，自由轮廓使用简洁的贝塞尔曲线。渐变使用原生 SVG 渐变，主要对象按语义分组。最终文件中的画面由矢量对象组成，不含嵌入或链接的位图。

Skill 会根据参考图选择合适的重建模式。

- `geometric-flat` 适合规则几何、大色块，以及对齐或重复排列的元素。
- `clean-flat` 适合带有自由曲线的物体，也适合几何形状与不规则轮廓混合的场景。

## 怎么使用

把仓库中的 `skill/clean-vector-reconstruction` 文件夹放到你使用的 AI Agent 的 Skill 目录，然后提供参考图和输出位置。如果有目标编辑器、尺寸要求或素材使用限制，也一起说明。

可以这样发起任务。

> 用 clean-vector-reconstruction 把这张插画重建成可编辑的 SVG，输出到指定文件夹。后续我会在 Adobe Illustrator 中调整，请保留主要物体的分组，并生成预览图。

## 会得到哪些文件

主要输出包括分层 SVG、普通 SVG 和预览图。

分层 SVG 保留便于编辑的分组，适合在 Illustrator 中继续调整。普通 SVG 使用更精简的结构，方便在其他支持 SVG 的工具中使用。两份文件呈现相同的画面。

此外，还会保留叠加对比图、差异图和检查报告，帮助你对照参考图检查结果。

交付前，工作流会检查 SVG 结构、画布尺寸和位图引用等问题。你可以先看预览与对比图，确认构图、轮廓和颜色，再到 Illustrator 里检查对象选择与编辑是否顺手，按实际用途做最后的调整。

具体方法见 [重建方法](docs/methodology.md)、[检查方式](docs/validation.md) 和 [适用范围](docs/limitations.md)。

## 许可证与示例素材

本项目的软件和文档采用 [MIT License](LICENSE)。

示例图片的来源与使用条件见各案例说明。使用这些素材时，请遵循对应的授权要求。
