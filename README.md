# Design

# Usage

To create a plot in a Conda environment, the following Python packages from `conda-forge` are required:
- bitstring
- matplotlib
- python
- scipy

To generate the Gnuplot data files, run the command
```bash
python piecewise_smooth_streamlines/piecewise_smooth_field.py
```
which will generate a directory `streamplot` with all the `.dat` files. To plot the image, call
```bash
gnuplot bifield_streamlines.plt
```
which will generate 2 plot files, `test.png` and `test.svg`. Use the command
```bash
gio open <file name>
```
to open any of the resulting files.
