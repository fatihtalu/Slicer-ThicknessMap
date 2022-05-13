# Slicer-ThicknessMap
Thickness map generation extension for 3d Slicer
The purpose of this extension is to generate thickness maps of segments from MR or CT data.
The thickness value of any desired point on the generated model can be obtained by using landmarks or the entire thickness map model can be exported to a file.
This extension includes the implementation of the approach shown in link [1].
Patent: There is no patent related to the extension.
License: The Slicer License.

# Usage at 3dSlicer
1) Install ThicknessMap extension by using the Extension Wizard or Manuel
2) Load a MRI or CT data to 3D Slicer (you can use Sample Data extension)
3) Open ThicknessMap extension and select a 3D input volume
4) Set a threshold value to get a segment from the 3D volume and click Apply Segmentation button. You can repeat this process until you find the most suitable threshold value
7) Click the Apply Thickness button to generate Thickness Map model of the segment

# Algorithm
1) Export Label-Map and Model from the segmentation
2) A medial surface from the label-map is created by using the BinaryThinningImageFilter
3) A distance map from the medial surface is created by using the DanielssonDistanceMapImageFilter (Binary=Yes and ImageSpacing=Yes)
4) A thickness model with the distance map is generated by using the Probe Volume with Model.

# Patent and Licence
There is no patent and licence of the extension. The method is belong to [1]. This extension is made just to be able to use it in 3d Slicer. You can see the step-by-step screen prints of the method from the link:

[1] Fluvio Lobo, Most Efficient Way of Creating a Thickness Map
https://discourse.slicer.org/t/most-efficient-way-of-creating-a-thickness-map/18203/3    
    
# An example extension output
![2](https://user-images.githubusercontent.com/22032994/158332495-b367f4e5-7c48-4864-9b43-cb600989ee3d.PNG)
