<p align="center">
  <a href="README.md"><strong>English</strong></a> |
  <a href="README.zh-CN.md">简体中文</a>
</p>

# Clean Vector Reconstruction

Rebuild raster illustrations as clean, editable SVGs, ready for further work in Adobe Illustrator.

Clean Vector Reconstruction is a Skill for AI agents working with flat, semi-flat, and geometric colour-block illustrations. It reads the reference image, works out the composition and individual objects, then rebuilds the artwork with vector shapes.

The workflow considers both visual fidelity and what happens when you open the file to edit it. Main objects stay individually selectable, colours and gradients remain adjustable, and paths are kept simple enough to work with.

## What images work well

Illustrations with clear colour boundaries and recognisable object structures are a good place to start. These include geometric artwork, still lifes, and scenes built around architecture, furniture, or shelving.

A busy scene can work well too. If the objects have readable shapes and clear overlaps, the scene can be broken down and rebuilt piece by piece. Repeated elements can share consistent dimensions and spacing.

Photography, heavy brushwork, and dense textures fall outside the Skill's main scope. Subjects that depend on subtle contours, such as fingers, hair, or complex animal poses, also tend to need more manual adjustment.

## See the results

These five examples show the reference images alongside their reconstructions.

### Geometric Harvest

| Reference | Reconstructed SVG |
| --- | --- |
| ![Geometric Harvest reference](examples/geometric-harvest/reference.png) | [![Geometric Harvest reconstruction](examples/geometric-harvest/preview.png)](examples/geometric-harvest/reconstruction-layered.svg) |

Broad colour blocks and a few gradients make this a good fit for reconstruction with simple geometric shapes.

### Still Life

| Reference | Reconstructed SVG |
| --- | --- |
| ![Still Life reference](examples/still-life/reference.png) | [![Still Life reconstruction](examples/still-life/preview.png)](examples/still-life/reconstruction-layered.svg) |

The fruit, vessel, leaves, and table are treated as separate objects. Curves retain the individual shapes of the fruit and leaves, making them easy to adjust later.

### Winter Street

| Reference | Reconstructed SVG |
| --- | --- |
| ![Winter Street reference](examples/winter-street/reference.png) | [![Winter Street reconstruction](examples/winter-street/preview.png)](examples/winter-street/reconstruction-layered.svg) |

The buildings and roadway are positioned first, followed by lighting and snow. Even with many elements, the scene can be organised into clear groups that follow its structure.

### Kitchen Interior

| Reference | Reconstructed SVG |
| --- | --- |
| ![Kitchen Interior reference](examples/kitchen-interior/reference.png) | [![Kitchen Interior reconstruction](examples/kitchen-interior/preview.png)](examples/kitchen-interior/reconstruction-layered.svg) |

Repeated cabinet doors and vessels can be handled together to keep proportions and spacing consistent.

### Market Shelf

| Reference | Reconstructed SVG |
| --- | --- |
| ![Market Shelf reference](examples/market-shelf/reference.png) | [![Market Shelf reconstruction](examples/market-shelf/preview.png)](examples/market-shelf/reconstruction-layered.svg) |

The shelving comes first, then the products, containers, and crates on each level. Repeated objects share a common construction while keeping the local variations in the reference.

## How it works

Start with the whole image, build the objects, then add the details.

Reconstruction begins with the canvas proportions and large colour regions. The main objects are positioned with their spacing and overlaps in place. Once the composition is established, the workflow refines individual contours and adds gradients, strokes, and smaller details.

Regular shapes use native SVG rectangles, circles, and ellipses wherever practical. Freeform contours use concise Bézier paths. Gradients are native SVG gradients, and main objects are grouped semantically. The finished artwork consists of vector objects, with no embedded or linked raster images.

The Skill selects a reconstruction mode based on the reference.

- `geometric-flat` suits regular geometry, broad colour blocks, and aligned or repeating elements.
- `clean-flat` suits objects with freeform curves, including scenes that mix geometric and irregular shapes.

## How to use it

Copy the repository's `skill/clean-vector-reconstruction` folder into your AI agent's Skill directory, then provide a reference image and an output location. Include your intended editor, size requirements, or any restrictions on using the source material.

A request can be as simple as this.

> Use clean-vector-reconstruction to rebuild this illustration as an editable SVG and save it to the specified folder. I'll continue editing in Adobe Illustrator, so keep the main objects grouped and generate a preview.

## What you get

The main outputs are a layered SVG, a plain SVG, and a preview image.

The layered SVG keeps useful editing groups for further work in Illustrator. The plain SVG uses a simpler structure for use in other SVG tools. Both versions contain the same artwork.

The workflow also saves an overlay, a difference image, and check reports to help you compare the result with the reference.

Before delivery, it checks the SVG structure, canvas dimensions, and raster references. Start with the preview and comparison images to review the composition, contours, and colours. Then open the SVG in Illustrator, check how selection and editing feel, and make the final adjustments for your intended use.

For more detail, see [Methodology](docs/methodology.md), [Validation](docs/validation.md), and [Limitations](docs/limitations.md).

## License and example assets

The project's software and documentation are released under the [MIT License](LICENSE).

See each example's notes for image sources and usage terms. Follow the relevant permissions when using those assets.
