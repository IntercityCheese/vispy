import sys
from PySide6.QtWidgets import QApplication
import widgets_elements.vispyWindowLib as vwl

app = QApplication(sys.argv)
vm = vwl.VariableManagerWidget()
# add a few variables
vm.add_variable('test_a', 'String')
vm.add_variable('test_b', 'Float')
vm.add_variable('test_c', 'Integer')

# find a widget and change its type repeatedly
all_names = [n for n in vm._get_all_variable_names()]
print('initial names:', all_names)

# pick the first widget
# find the widget instance
w = None
for type_key, group in vm._type_groups.items():
    for i in range(group.childCount()):
        child = group.child(i)
        ww = vm.tree.itemWidget(child, 0)
        if ww and ww.name == 'test_a':
            w = ww
            print('found widget for test_a')
            break
    if w:
        break

if not w:
    print('widget not found')
    sys.exit(1)

# Try changing its type multiple times
try:
    print('changing type to Float')
    vm.update_variable_type_widget(w, 'Float')
    print('changing type to Boolean')
    vm.update_variable_type_widget(w, 'Boolean')
    print('changing type back to String')
    vm.update_variable_type_widget(w, 'String')
    print('type changes completed')
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception during type changes:', e)

print('OK')
# Not starting the full event loop to keep test short
