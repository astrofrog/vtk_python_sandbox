import vtk
from numpy import *

from astropy.io import fits

#------------Load volume data from FITS file-----------------
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
 
# The following class is used to store transparencyv-values for later retrival. In our case, we want the value 0 to be
# completly opaque whereas the three different cubes are given different transperancy-values to show how it works.
alphaChannelFunc = vtk.vtkPiecewiseFunction()
alphaChannelFunc.AddPoint(0, 0.0)
alphaChannelFunc.AddPoint(50, 0.05)
alphaChannelFunc.AddPoint(100, 0.1)
alphaChannelFunc.AddPoint(150, 0.2)
 
# This class stores color data and can create color tables from a few color points. For this demo, we want the three cubes
# to be of the colors red green and blue.

colorFunc = vtk.vtkColorTransferFunction()
colorFunc.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorFunc.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
colorFunc.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
colorFunc.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
colorFunc.AddRGBPoint(255.0, 0.0, 0.2, 0.0)

# colorFunc = vtk.vtkColorTransferFunction()
# colorFunc.AddRGBPoint(1, 0.0, 0.0, 0.0)
# colorFunc.AddRGBPoint(50, 1.0, 0.0, 0.0)
# colorFunc.AddRGBPoint(100, 0.0, 1.0, 0.0)
# colorFunc.AddRGBPoint(150, 0.0, 0.0, 1.0)
 
# The preavius two classes stored properties. Because we want to apply these properties to the volume we want to render,
# we have to store them in a class that stores volume prpoperties.
volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorFunc)
volumeProperty.SetScalarOpacity(alphaChannelFunc)
 
# This class describes how the volume is rendered (through ray tracing).
compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
# We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
volumeMapper = vtk.vtkVolumeRayCastMapper()
volumeMapper.SetVolumeRayCastFunction(compositeFunction)
volumeMapper.SetInputConnection(dataImporter.GetOutputPort())
 
# The class vtkVolume is used to pair the preaviusly declared volume as well as the properties to be used when rendering that volume.
volume = vtk.vtkVolume()
volume.SetMapper(volumeMapper)
volume.SetProperty(volumeProperty)

#----------Plot Points upon volume rendering ---------------
class VtkPointCloud:

    def __init__(self, zMin=-10.0, zMax=10.0, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtk.vtkPolyData()
        self.clearPoints()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        # TODO: for change colormap
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtk.vtkActor()
        self.vtkActor.SetMapper(mapper)

    def addPoint(self, point, size=10):
        if self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints:
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
            self.vtkActor.GetProperty().SetPointSize(size)
        else:
            r = random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()
        self.vtkActor.Modified()

    def clearPoints(self):
        self.vtkPoints = vtk.vtkPoints()
        self.vtkCells = vtk.vtkCellArray()
        self.vtkDepth = vtk.vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')

pointCloud = VtkPointCloud()
inputFile='cloud_catalog_july14_2015.fits'
# data = numpy.genfromtxt(inputFile, delimiter=' ')
tbdata=fits.open(inputFile)[1].data
xyz=zeros((50, 3))
xyz[:, 0] = random.rand(50)*data_matrix.shape[2]
xyz[:, 1] = random.rand(50)*data_matrix.shape[1]
xyz[:, 2] = random.rand(50)*data_matrix.shape[0]

numberOfPoints = tbdata.shape[0]

for i in xrange(50):
    
    print('point pos', xyz[i][:3])
    # pointCloud.addPoint(xyz[i][:3])
    pointCloud.addPoint(xyz[i][:3])
 
#-------------- Add isosurface ----------------
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

#--------------Set up renderer and render window-------------------
# With almost everything else ready, its time to initialize the renderer and window, as well as creating a method for exiting the application
renderer = vtk.vtkRenderer()
renderWin = vtk.vtkRenderWindow()
renderWin.AddRenderer(renderer)
renderInteractor = vtk.vtkRenderWindowInteractor()
renderInteractor.SetRenderWindow(renderWin)
 
# We add the volume to the renderer ...
renderer.AddVolume(volume)
# add the points to the renderer ...
renderer.AddActor(pointCloud.vtkActor)
# add isosurface to the renderer
renderer.AddActor(actorBone)

# ... set background color to white ...
renderer.SetBackground(0,0,0)
# ... and set window size.
renderWin.SetSize(400, 400)
 
# A simple function to be called when the user decides to quit the application.
def exitCheck(obj, event):
    if obj.GetEventPending() != 0:
        obj.SetAbortRender(1)
 
# Tell the application to use the function as an exit check.
renderWin.AddObserver("AbortCheckEvent", exitCheck)
 
renderInteractor.Initialize()
# Because nothing will be rendered without any input, we order the first render manually before control is handed over to the main-loop.
renderWin.Render()
renderInteractor.Start()