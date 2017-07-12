# import Tkinter
import os
import vtk
from numpy import *
from astropy.io import fits

TRAVIS = os.environ.get('TRAVIS', 'false') == 'true'

# from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

# -------read fits file------
# We begin by creating the data we want to render.
# For this tutorial, we create a 3D-image containing three overlaping cubes.
# This data can of course easily be replaced by data from a medical CT-scan or anything else three dimensional.
# The only limit is that the data must be reduced to unsigned 8 bit or 16 bit integers.

data_matrix = fits.open('l1448_13CO.fits')[0].data #pyfits.getdata('L1448_13CO.fits.gz')
# data_matrix = data_matrix[145:245,:,:]
data_matrix[data_matrix < 0.5] = 0.
data_matrix = (data_matrix * 100).astype(uint8)
nz, ny, nx = data_matrix.shape

# For VTK to be able to use the data, it must be stored as a VTK-image. This can be done by the vtkImageImport-class which
# imports raw data and stores it.
dataImporter = vtk.vtkImageImport()
# The preaviusly created array is converted to a string of chars and imported.
data_string = data_matrix.tostring()
dataImporter.CopyImportVoidPointer(data_string, len(data_string))
# The type of the newly imported data is set to unsigned char (uint8)
dataImporter.SetDataScalarTypeToUnsignedChar()
# Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer
# must be told this is the case.
dataImporter.SetNumberOfScalarComponents(1)
# The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
# simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
# I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
# VTK complains if not both are used.
dataImporter.SetDataExtent(0, nx-1, 0, ny-1, 0, nz-1)
dataImporter.SetWholeExtent(0, nx-1, 0, ny-1, 0, nz-1)
# ---------read fits file done----------

# Prepare to read the file
# readerVolume = vtk.vtkImageReader()
# readerVolume.SetDataScalarType( vtk.VTK_UNSIGNED_SHORT )
# readerVolume.SetFileDimensionality( 3 )
# readerVolume.SetDataExtent ( 0,255, 0,255, 0,576)
# readerVolume.SetDataSpacing( 1,1,1 )
# readerVolume.SetNumberOfScalarComponents( 1 )
# readerVolume.SetDataByteOrderToBigEndian()
# readerVolume.SetFileName( "./Female.raw" )

# Extract the region of interest
# voiHead = vtk.vtkExtractVOI()
# voiHead.SetInput( readerVolume.GetOutput() )
# voiHead.SetVOI( 0,255, 60,255, 0,100 )
# voiHead.SetSampleRate( 1,1,1 )

# Generate an isosurface
# UNCOMMENT THE FOLLOWING LINE FOR CONTOUR FILTER
# contourBoneHead = vtk.vtkContourFilter()
contourBoneHead = vtk.vtkMarchingCubes()
# contourBoneHead.SetInput( dataImporter.GetOutput() )
contourBoneHead.SetInputConnection( dataImporter.GetOutputPort() )
contourBoneHead.ComputeNormalsOn()
contourBoneHead.SetValue( 0, 150 )  # Bone isovalue

# Take the isosurface data and create geometry
geoBoneMapper = vtk.vtkPolyDataMapper()
# geoBoneMapper.SetInput( contourBoneHead.GetOutput() )
geoBoneMapper.SetInputConnection( contourBoneHead.GetOutputPort() )
geoBoneMapper.ScalarVisibilityOff()

# Take the isosurface data and create geometry
actorBone = vtk.vtkLODActor()
actorBone.SetNumberOfCloudPoints( 1000000 )
actorBone.SetMapper( geoBoneMapper )
actorBone.GetProperty().SetColor( 1, 1, 1 )

# Create renderer
ren = vtk.vtkRenderer()
ren.SetBackground( 0.329412, 0.34902, 0.427451 ) #Paraview blue
ren.AddActor(actorBone)

# Create a window for the renderer of size 250x250
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetSize(250, 250)

# Set an user interface interactor for the render window
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Start the initialization and rendering
iren.Initialize()
renWin.Render()

if not TRAVIS:
    iren.Start()
