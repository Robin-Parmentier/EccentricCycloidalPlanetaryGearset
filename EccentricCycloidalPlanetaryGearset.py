# Assuming you have not changed the general structure of the template no modification is needed in this file.
from . import commands
from .lib import fusion360utils as futil
import adsk.core, adsk.fusion, adsk.cam, traceback

#global variables
ui = adsk.core.UserInterface.cast(None)
app = adsk.core.Application.cast(None)
units = ""

#command dialogue options
unitsDropdown = adsk.core.DropDownCommandInput.cast(None)
planetOrbitDiameter = adsk.core.ValueCommandInput.cast(None)
planetDiameter = adsk.core.ValueCommandInput.cast(None)
gearRatio = adsk.core.ValueCommandInput.cast(None) #assume driving sun, driven planets

handlers = []

def run(context):
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDef = ui.commandDefinitions.itemById('EccentricCycloidalGearsetAddin')
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition('EccentricCycloidalGearsetAddin', 
                                                   'Eccentric Cycloidal Gearset', 
                                                   'generates an eccentric cycloidal gearset')
        
        # Connect to the command created event.
        onCommandCreated = CycloidalCommandCreatedEventHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        #execute the command
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CycloidalCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class CycloidalCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(app.activeProduct)
            if not des:
                ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
            
            #get default units
            defaultUnits = des.unitsManager.defaultLengthUnits
            global units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                units = 'in'
            else:
                units = 'mm'
            unitsAttrib = des.attributes.itemByName('EccentricCycloidalGearset', 'units')
            if unitsAttrib:
                units = unitsAttrib.value

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            #set default orbit diameter
            if units == 'mm':
                orbitDiameter = 100
            else:
                orbitDiameter = 4
            orbitDiameterAttrib = des.attributes.itemByName('EccentricCycloidalGearset', 'planetOrbitDiameter')
            if orbitDiameterAttrib:
                orbitDiameter = float(orbitDiameterAttrib.value)   

            global unitsDropdown, planetOrbitDiameter, planetDiameter, gearRatio

            # --------- add command dialogue
            unitsDropdown = inputs.addDropDownCommandInput('units', 'units', adsk.core.DropDownStyles.TextListDropDownStyle)
            if units == 'in':
                unitsDropdown.listItems.add('in', True)
                unitsDropdown.listItems.add('mm', False)
            else:
                unitsDropdown.listItems.add('in', False)
                unitsDropdown.listItems.add('mm', True)

            planetOrbitDiameter = inputs.addValueInput('planetOrbitDiameter', 'planet orbit diameter', units, adsk.core.ValueInput.createByReal(float(orbitDiameter)))

            # Connect to the command related events.
            onExecute = CycloidalCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)        
            
            onInputChanged = CycloidalCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)     

            onDestroy = CycloidalCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)
            

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class CycloidalCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('In command execute event handler.')

class CycloidalCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            global units
            if changedInput.id == 'units':
                if unitsDropdown.selectedItem.name == 'in':
                    units = 'in'
                elif unitsDropdown.selectedItem.name == 'mm':
                    units = 'mm'

                #update values
                planetOrbitDiameter.value = planetOrbitDiameter.value

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('MyButtonDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('MyButtonDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	