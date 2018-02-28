
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino
import math
from time import sleep

refresh_time = 0.1

F0_GUID = "f5b64d4e-911e-41ee-bee8-7f51323c3c5f"
F1_GUID = "db88242f-867b-41d2-b0a8-90a532a104eb"
F2_GUID = "925f05d1-1985-4a58-8f03-a2cde8a1851c"
F3_GUID = "ceb9bd12-8f4a-40e5-bf58-602e6e19bd5b"
F4_GUID = "35d6ef37-09f8-457a-bb6c-b467a5ddab68"
F5_GUID = "9aeb1ae9-ce09-4d3b-a3ae-c11ef6b81b81"
F6_GUID = "f9b9c190-bab3-4b8a-9217-4d196e5b0058"
F7_GUID = "7e4f279c-ec7c-4036-8166-478b600ace35"
GUID_ARR = [F0_GUID, F1_GUID, F2_GUID, F3_GUID, 
            F4_GUID, F5_GUID, F6_GUID, F7_GUID]

ROTATE_GUID = "1632b9c9-8fac-4688-9110-fb14873d68e9"
VARIANCE_GUID = "e9450790-36ee-4f45-beec-c98c5efd6b06"

GST_STATIC = 0
GST_COVER = 1
GST_SPIN_RIGHT = 2
GST_SPIN_LEFT = 3
GST_COVER_OFF = 4

sensor_number = 8
filename = "C:\\HCI-final-project-master\\python\\arduino_buffer.txt"
angle_diff = math.pi / 20
current_angle = 0
is_covered = False


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
    if not is_covered:
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
            
    if gesture == GST_COVER:
        is_covered = True
    
    if gesture == GST_COVER_OFF:
        is_covered = False
    
    if (gesture == GST_SPIN_RIGHT):
        current_angle += angle_diff
        if (current_angle > 2 * math.pi):
            current_angle = 0
        gh.SetSliderValue(ROTATE_GUID, current_angle)
    
    if (gesture == GST_SPIN_LEFT):
        current_angle -= angle_diff
        if (current_angle <= 0 ):
            current_angle = 2 * math.pi
        gh.SetSliderValue(ROTATE_GUID, current_angle)
    
    # update view
    gh.RunSolver("virtualAgent2_Gal.gh")
    
    Rhino.RhinoApp.Wait()
    if sc.escape_test(False):
        print "ESC pressed "
        break


