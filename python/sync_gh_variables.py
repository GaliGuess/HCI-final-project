
import rhinoscriptsyntax as rs
import Rhino
import Grasshopper as gh
import time

GUID_SLIDER_1 = "57962757-bbc1-4db9-960d-f595f3113dde"

rs.EnableRedraw(True)

for i in range(100):
    gh.SetSliderValue(GUID_SLIDER_1, 0)
    time.sleep(1)

print("Done.")
print(time.ctime() + ": Done.")
