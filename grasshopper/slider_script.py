
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math
from time import sleep

refresh_time = 0.1

F0_GUID = "80f4774d-1225-4aec-84f3-55fd4990833d"
F1_GUID = "b04a6c7b-b04d-488b-9ab7-9ab99d8f4405"
F2_GUID = "57bad36d-e431-4fa2-8c56-bfc332b37074"
F3_GUID = "4498d06a-f050-4ccb-a548-e579fb053c3f"
F4_GUID = "59887ad7-a1ce-4f33-8142-22cbfddadc2e"
F5_GUID = "6b60494d-baaa-4ba2-8f6d-ceac3fcb666b"
F6_GUID = "811bd9cb-dd5a-44ba-a36c-28acfff21cb7"
F7_GUID = "c681f240-b1bc-4032-b9c7-0a6b5017f1fc"
GUID_ARR = [F0_GUID, F1_GUID, F2_GUID, F3_GUID, 
            F4_GUID, F5_GUID, F6_GUID, F7_GUID]

ROTATE_GUID = "1632b9c9-8fac-4688-9110-fb14873d68e9"
VARIANCE_GUID = "e9450790-36ee-4f45-beec-c98c5efd6b06"

GST_STATIC = 0
GST_COVER = 1
GST_SPIN_RIGHT = 2
GST_SPIN_LEFT = 3

sensor_number = 8
filename = "C:\\HCI-final-project-master\\python\\arduino_buffer.txt"
angle_diff = math.pi / 20
current_angle = 0


def isclose(a, b, tol=1e-5):
    return abs(a - b) <= tol


rs.EnableRedraw(True)
gh = Rhino.RhinoApp.GetPlugInObject("Grasshopper")

#count = [1,2,3,4,5,6,7,8]
var_count = 2
var_down = False
var_speed = 0.05

while True:
    
    # changing random sin function
    gh.SetSliderValue(VARIANCE_GUID, var_count)
    if var_down:
        var_count -= var_speed
    else:
        var_count += var_speed
    
    if isclose(var_count, 2) or isclose(var_count, 3):
        var_down = not var_down
    
    # reading file again
    file = open(filename, "r")
    lines = file.readlines()
    
    if (len(lines) == 2):
        try:
            gesture = int(lines[0])
        except:
            print(lines[0])           
    else:
        gesture = -1
    
    file.close()
    
    # check gesture
    if (gesture == GST_STATIC):
        data = lines[1].split(",")
        for i in range(sensor_number):
            gh.SetSliderValue(GUID_ARR[i], float(data[i]))
            
            # for testing continuous updates
#            gh.SetSliderValue(GUID_ARR[i], count[i])
#            count[i] += 0.1
#            if count[i] > 10:
#                count[i] = 0
            
    elif (gesture == GST_COVER):
        pass
    
    elif (gesture == GST_SPIN_RIGHT):
        current_angle += angle_diff
        if (current_angle > 2 * math.pi):
            current_angle = 0
        gh.SetSliderValue(ROTATE_GUID, current_angle)
    
    elif (gesture == GST_SPIN_LEFT):
        current_angle -= angle_diff
        gh.SetSliderValue(ROTATE_GUID, current_angle)
    
    # update view
    gh.RunSolver("virtualAgent2_Gal.gh")
    
    Rhino.RhinoApp.Wait()
    if sc.escape_test(False):
        print "ESC pressed "
        break


