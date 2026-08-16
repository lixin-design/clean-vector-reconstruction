<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md"><strong>简体中文</strong></a>
</p>

# Clean Vector Reconstruction

Clean Vector Reconstruction 是一套小型工作流，用来把扁平或半扁平的位图插画重建成可编辑的 SVG。它更适合色块边界清楚、几何关系明确，或有重复视觉元素的画面。

这里不追求逐像素描摹。更重要的是保留画面里的关键关系，让结果在 Adobe Illustrator 中仍然看得懂、改得动。

## 适合做什么

工作流会把参考图重建为有明确含义的矢量几何：能用原生图元的地方就用图元，其余部分用简洁的 Bézier 路径，再用普通 SVG 的填色、描边、渐变和分组组织起来。最终 SVG 不嵌入或链接位图。

色块插画、静物、结构清楚的室内、建筑场景，以及货架这类重复系统，都是合适的起点。画面复杂并不等于不适合；只要主要部分能拆清楚，边界看得明白，空间骨架或重复规律比较稳定，复杂场景也可以做得很好。

它不是通用的自动矢量化工具，也不以像素级一致为目标。人物肢体、手、头发、姿态复杂的动物、严重遮挡关系，或依赖笔触和纹理的画面，往往需要更谨慎地处理，也可能需要更多手工绘制。

## 示例

下面是五个有代表性的示例，并不是对准确度的承诺。每一组把参考图和可编辑 SVG 放在一起，配一句说明，讲清这个画面为什么适合这样重建。

### Geometric Harvest

| 参考图 | 重建 SVG |
| --- | --- |
| ![Geometric Harvest 参考图](examples/geometric-harvest/reference.png) | [![Geometric Harvest 重建图](examples/geometric-harvest/preview.png)](examples/geometric-harvest/reconstruction-layered.svg) |

清晰的几何色块、少量渐变和共用边界，让画面的构造关系很容易看出来。

### Still Life

| 参考图 | 重建 SVG |
| --- | --- |
| ![Still Life 参考图](examples/still-life/reference.png) | [![Still Life 重建图](examples/still-life/preview.png)](examples/still-life/reconstruction-layered.svg) |

水果、器皿、叶子和桌面彼此分得清楚，也保留了少量可以控制的有机轮廓。

### Winter Street

| 参考图 | 重建 SVG |
| --- | --- |
| ![Winter Street 参考图](examples/winter-street/reference.png) | [![Winter Street 重建图](examples/winter-street/preview.png)](examples/winter-street/reconstruction-layered.svg) |

街景元素不少，但建筑、道路、灯光和积雪可以拆成一组清楚的结构对象来处理。

### Kitchen Interior

| 参考图 | 重建 SVG |
| --- | --- |
| ![Kitchen Interior 参考图](examples/kitchen-interior/reference.png) | [![Kitchen Interior 重建图](examples/kitchen-interior/preview.png)](examples/kitchen-interior/reconstruction-layered.svg) |

橱柜、搁架、电器和一组重复的小物件先把室内空间搭稳，再补局部细节。

### Market Shelf

| 参考图 | 重建 SVG |
| --- | --- |
| ![Market Shelf 参考图](examples/market-shelf/reference.png) | [![Market Shelf 重建图](examples/market-shelf/preview.png)](examples/market-shelf/reconstruction-layered.svg) |

货架、容器、商品分组和木箱可以作为一个重复系统来整理，而不是零散地逐个拼出来。

## 工作方式

先确定画布、大色块、间距、遮挡关系和主要几何，再重建有意义的对象；构图稳住以后，再处理小细节。

附带的 Skill 有两种实用模式。`geometric-flat` 用于对齐色块、重复单元、规则几何和大面积色域；`clean-flat` 用于可控的自由曲线和混合结构场景。输出交给人看之前，会检查 SVG 结构是否正常，以及是否混入了位图。

## 使用 Skill

把 `skill/clean-vector-reconstruction` 放到项目使用的 Skill 目录，再提供参考图、输出位置、目标编辑器和发布限制即可。Skill 会产出分层 SVG、普通 SVG 和预览图，并保留必要的检查信息；最终是否可用，仍由人来判断。

## 输出与审阅

分层 SVG 保留对编辑有帮助的分组；普通 SVG 用更简单的形式保留同一画面，方便兼容使用。两者都使用原生 SVG 几何和资源，不放置位图。

自动检查擅长发现结构问题，却不能替人判断画面是否自然，或剩下的工作究竟只是 Illustrator 里的局部调整，还是需要重画。这里仍然要靠目视审阅。

更多说明见 [Methodology](docs/methodology.md)、[Validation](docs/validation.md) 和 [Limitations](docs/limitations.md)。

## 许可证与示例素材

本仓库中由项目作者提供的软件和文档采用 [MIT License](LICENSE)。示例中的视觉素材另有来源和使用说明；复制、修改或再分发前，请先阅读对应案例的说明。
