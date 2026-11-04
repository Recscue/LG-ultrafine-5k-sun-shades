# LG-ultrafine-5k-sun-shades
3D model for 3D printed sun shade custom designed for two 27" LG Ultrafine 5K monitors (27MD5KL-B), optimized for Bambu P2S

It clips onto each monitor's top edge, rises 8 in, reaches 7 in past each outer side, and carries a shelf for a Logitech MX Brio webcam where the monitors meet.

**3D viewer:** [recscue.github.io/LG-ultrafine-5k-sun-shades](https://recscue.github.io/LG-ultrafine-5k-sun-shades/). Drag to orbit, scroll to zoom.

![Front view](renders/01-front.png)

## Files

- `print-files/`: everything to print. Start with `print-files/READ-ME-FIRST.txt`.
  - `step-1_test-prints/`: the joint test pieces, all on one plate.
  - `step-2_full-shield/`: one complete shield at each joint size (0.10, 0.15, 0.20 mm), split into `left-monitor/` and `right-monitor/`. Print only the folder matching the test piece that fit best.
- `PRINTING.md`: print settings, assembly steps and the measurements to check before printing.
- `renders/`: still views of the spine, seams, corner and webcam shelf.
- `src/`: the parametric model. `python src/build.py` regenerates the STLs (needs `manifold3d`, `trimesh`, `numpy`, `scipy`).

![Webcam shelf](renders/10-webcam.png)
