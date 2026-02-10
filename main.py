import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QGridLayout, QLabel, QComboBox, QPlainTextEdit
import numpy as np
from PySide6.QtCore import Qt, QTimer
import pyqtgraph as pg


class ControlPanel(QWidget):
    class RecordingContainer(QWidget):
        def __init__(self):
            super().__init__()
           
            self.layout = QHBoxLayout()
            self.setLayout(self.layout)
            self.start_button = QPushButton("Start Recording")
            self.stop_button = QPushButton("Stop Recording")
            self.layout.addWidget(self.start_button)
            self.layout.addWidget(self.stop_button)
    def __init__(self):
        super().__init__()
        self.live_updates = True
        self.plot_widgets = [] # Internal reference to plotwidgets. Will be added by Main Window, so control panel can access and read the plots
        self.setMinimumWidth(250)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.title = QLabel("Control Panel")
        self.title.setAlignment(Qt.AlignCenter)
        self.duration_selection = QLabel("Test Duration Selection") #QLabel is just a text label
        self.duration_selection.setAlignment(Qt.AlignCenter)
        self.duration = QComboBox() #Combobox is a dropdown menu
        self.duration.addItems(["10 Minutes", "30 Minutes", "1 Hour", "2 Hours", "3 Hours", "4 Hours", "8 Hours", "12 Hours", "24 Hours"]) #Various durations
        self.recording_container = self.RecordingContainer()
        self.test_status = QLabel("Test Status: Not Active")
        self.test_status.setAlignment(Qt.AlignCenter)
        self.scope_toggle = QPushButton("Toggle Live Updates") # Button to toggle the scope view, which is updated live
        self.scope_toggle.clicked.connect(self.toggle_scope)
        # Connecting the buttons to functions
        self.recording_container.start_button.clicked.connect(self.start_recording)
        self.recording_container.stop_button.clicked.connect(self.stop_recording)


        #Now that all the widgets exist, add them to the layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.scope_toggle)
        self.layout.addWidget(self.duration_selection)
        self.layout.addWidget(self.duration)
        self.layout.addWidget(self.recording_container)
        self.layout.addWidget(self.test_status)
        #Stopping everything from expanding to the full height of the control panel
        self.layout.addStretch() 
    def toggle_scope(self):
        for plot_widget in self.plot_widgets:
            plot_widget.x_data.clear()
            plot_widget.y_data.clear()
        if self.live_updates:
            self.live_updates = False
            self.scope_toggle.setText("Enable Live Updates")
        else:
            self.live_updates = True
            self.scope_toggle.setText("Disable Live Updates")

    def start_recording(self):
        self.test_status.setText("Test Status: Active")
        pass
    def stop_recording(self):
        self.test_status.setText("Test Status: Not Active")
        pass
    
    def add_button(self, button):
        self.layout.addWidget(button)
class PlotWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.title = ""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget) # The layout will own the canvas we made, AKA the grapph
        self.setLayout(layout) # Use our layout in this widget
        #Storing the data
        self.x_data = []
        self.y_data = []
        self.line = self.plot_widget.plot(self.x_data, self.y_data, pen=pg.mkPen(color='y', width=1.4)) # Line that will be updated based on data, similair to a scope trace
    
    def configure_plot(self, xaxis_label, yaxis_label, title):
        self.plot_widget.setLabel('left', yaxis_label)
        self.plot_widget.setLabel('bottom', xaxis_label)
        self.plot_widget.setTitle(title)
    
    def update_plot(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)
        self.x_data = self.x_data[-100:] # Rotating buffer so the graph doesn't get too crowded
        self.y_data = self.y_data[-100:]
        self.line.setData(self.x_data, self.y_data) # Update the line with new data

class MainWindow(QMainWindow):
    class PlotHolder(QWidget):
        #Container for the plots as well as serial logger, using grid layout
        def __init__(self):
            super().__init__()
            self.layout = QGridLayout()
            self.setLayout(self.layout)
    class SerialLogger(QWidget):
        def __init__(self):
            #Just a console preview to make sure serial data is being read
            super().__init__()
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)
            self.text_box = QPlainTextEdit()
            self.text_box.setReadOnly(True)
            self.text_box.setMinimumHeight(150)

            self.layout.addWidget(self.text_box)
            self.layout.addStretch()
        
        def update_serial_data(self, data): # Called everytime serial is read
            self.text_box.appendPlainText(data)
            if self.text_box.document().lineCount() > 100: # Limit the number of lines in the logger to prevent memory issues
                cursor = self.text_box.textCursor()
                #Select the start of the textbox
                cursor.movePosition(cursor.MoveOperation.Start)
                cursor.select(cursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText() # Delete the selected line
                cursor.deleteChar() # Deleting invisible \ (newline) character


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waste Heat Recovery System")
        self.timer = QTimer()

        self.timer.setInterval(20) # Set the timer to update every 20 milliseconds (50 updates per second)  
        self.time = 0 # Internal time tracking for dummy data
        self.timer.timeout.connect(self.read_serial)
        self.build_ui()
        self.timer.start() # Start the timer to read serial data and update plots

    def build_ui(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Roboto;}
            QMainWindow {
                background-color: #3C3C3C;
            }
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #F2C57C;
                color: black;
                border-radius: 2px;
                padding: 5px;
            }
            QComboBox {
                background-color: #F2C57C;
                           }
        """)
        center_widget = QWidget()
        self.setCentralWidget(center_widget)
        # Layout for the central widget. The central widget has possesion of the whole window, so we can use it to set the layout for the entire window.
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        center_widget.setLayout(self.layout)
        # Control Panel Config
        self.control_panel = ControlPanel()
        self.layout.addWidget(self.control_panel)
        
        
        # Plot window config
        self.plot_holder = self.PlotHolder()
        self.layout.addWidget(self.plot_holder)
        #Serial Logger config, owned by grid in pos 3,0
        self.serial_logger = self.SerialLogger()
        self.plot_holder.layout.addWidget(self.serial_logger, 3, 0, 1, 2) # Row 3, Column 0, Row Span 1, Column Span 2


        #Helper function to add plot widgets
    def add_plot(self, plot_widget, row=0, col=0):
        self.plot_holder.layout.addWidget(plot_widget, row, col)
        self.control_panel.plot_widgets.append(plot_widget) # Add the plot widget to the control panel's internal list for access when reading serial data


    def read_serial(self):
        # Read data from serial port and update plots, so long as live updates is enabled
        x, y = self.generate_dummy_data() # Replace with actual serial data reading
        if self.control_panel.live_updates:
            for i in range(self.plot_holder.layout.count()):
                plot_widget = self.plot_holder.layout.itemAt(i).widget()
                if isinstance(plot_widget, PlotWidget):
                    
                    self.serial_logger.update_serial_data(f"{plot_widget.title} Time: {x:.2f}s, Value: {y:.2f}") # Log the data to the serial logger
                    plot_widget.update_plot(x, y)
            pass

    def generate_dummy_data(self):
        self.time += 0.02 # Increment time by 20 milliseconds for each update
        return self.time, np.random.random() * 100  # Dummy data simulating a wave pattern
        


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    #Adding a bunch of placeholder plots
    plot1 = PlotWidget()

    plot1.configure_plot("X-axis", "Y-axis", "RPM")
    plot2 = PlotWidget()
    plot2.configure_plot("Time", "Value", "Water Vs Ambient Temperature")
    plot3 = PlotWidget()
    plot3.configure_plot("Time", "Value", "Voltage")
    plot4 = PlotWidget()
    plot4.configure_plot("Time", "Value", "Current")
    window.add_plot(plot1, 0, 0)
    window.add_plot(plot2, 0, 1)
    window.add_plot(plot3, 1, 0)
    window.add_plot(plot4, 1, 1)
    #Finally show the window
    window.show()



    sys.exit(app.exec_())

if __name__ == "__main__":    main()