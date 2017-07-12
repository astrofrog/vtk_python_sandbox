#!/bin/bash -xe

python vtk_isosurface.py
python vtk_line.py
python vtk_plane_selection.py
python vtk_points.py
python vtk_volume_points.py
python vtk_volume_points_iso.py
python vtk_with_numpy.py
python vtk_with_pyfits.py
python vtk_with_qt.py
python vtk_with_qt_and_pyfits.py
python HighlightPickedActor.py
