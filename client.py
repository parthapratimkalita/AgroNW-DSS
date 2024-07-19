#!/usr/bin/env python3
import os
import glob
import sys
import requests
import folium
import json
import io
import re
import explainable_plot
import create_field
import threading
from folium.plugins import Draw
from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QDesktopServices, QPixmap,QTextCursor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QVBoxLayout,QLabel, QTextBrowser, QWidget, QSizePolicy, QHBoxLayout, QFileDialog

def save_map_with_global_variable(map_object, file_path):
    data = io.BytesIO()
    map_object.save(data, close_file=False)
    map_html = data.getvalue().decode()

    # Add JavaScript to initialize the map variable
    map_html = map_html.replace('<head>', '<head><script>var map;</script>')
    map_html = map_html.replace('L.map(', 'map = L.map(')

    with open(file_path, 'w') as f:
        f.write(map_html)

def read_existing_map(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def load_existing_map(file_path):
    with open(file_path, 'r') as f:
        map_html = f.read()
    return map_html

def add_polygon_to_map(map_html, coordinates):
    # Create a new Folium map object
    existing_map_html = read_existing_map(map_html)
    m = folium.Map(location=[52.283333, 10.4515], zoom_start=8)


     # Add the existing map's HTML content to the new map
    m.get_root().html.add_child(folium.Element(existing_map_html))

    # Add the new polygon to the map
   
    polygon = folium.Polygon(locations=coordinates, color="red", fill=True)
    polygon.add_to(m)
    
    # Save the updated map to map.html
    save_map_with_global_variable(m, "map1.html")

    return m

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        uic.loadUi('QT_ui_interface/interface.ui', self)

        self.mainPages.setCurrentWidget(self.homePage)

        self.homeBtn.setStyleSheet("""
            border-left: 4px solid green; 
        """)



        # Connect the buttons' clicked signals to the button_clicked slot
        self.mapBtn.clicked.connect(lambda: self.button_clicked(self.mapBtn))
        self.homeBtn.clicked.connect(lambda: self.button_clicked(self.homeBtn))
        self.aboutBtn.clicked.connect(lambda: self.button_clicked(self.aboutBtn))
        self.settingsBtn.clicked.connect(lambda: self.button_clicked(self.settingsBtn))
        self.fieldBtn.clicked.connect(lambda: self.button_clicked(self.fieldBtn))
        self.fWmes.clicked.connect(lambda: self.button_clicked(self.fWmes))

        self.menuBtn.clicked.connect(self.toggle_left_menu)
        self.menuBtn.clicked.connect(self.animate_button)
        self.mapBtn.clicked.connect(self.go_to_map)
        self.homeBtn.clicked.connect(self.go_to_home)
        self.aboutBtn.clicked.connect(self.go_to_about)
        self.settingsBtn.clicked.connect(self.go_to_settings)
        self.fieldBtn.clicked.connect(self.go_to_field)
        self.fWmes.clicked.connect(self.go_to_fwmes)
        self.buttons = []

        self.explainBtn = QPushButton("Explain", self)
        self.explainBtn.setStyleSheet("""
            background-color: green; 
            border-radius: 10px; 
            text-align: center;
        """)
        self.explainBtn.hide()  # Hide the button initially
        self.tableWidget.cellClicked.connect(self.on_cellClicked)

        # Add a QLabel to display the image
        self.imageLabel = QLabel(self)
        self.imageLabel.hide()  # Hide the label initially

    # ...
    
        # Set a layout for mapPage
        self.mapPage.setLayout(QVBoxLayout())

        # Get a list of all JSON files in the database directory
        json_files = glob.glob('db/*.json')
        # Create a dictionary to store the polygons and their corresponding buttons
        self.polygons = {}

        self.polygons_cor = {}

        

        # Create a QWebEngineView, load the HTML file
        self.view = QWebEngineView()
        self.add_new_field_polygoan()

        self.fetch_wmes_data()


    def add_new_field_polygoan(self):
        json_files = glob.glob('db/*.json')

        # Create a Folium map with a default location
        m = folium.Map(location=[52.283333, 10.4515], zoom_start=8)

        for json_file in json_files:
            with open(json_file, 'r') as file:
                data = json.load(file)

            # Navigate to the polygon data
            try:
                polygon_wkt = data['value0']['ptr_wrapper']['data']['components'][1]['key']['ptr_wrapper']['data']['wkt']
            except KeyError:
                polygon_wkt = data['value0']['ptr_wrapper']['data']['components'][0]['key']['ptr_wrapper']['data']['wkt']
            match = re.findall(r'\d+.\d+', polygon_wkt) 

            lon = []
            lat = []
            for i in range(len(match)):
                if i%2 ==0:
                    lon.append(match[i])
                else:
                    lat.append(match[i])

            coordinates = []
            for i in range(len(lon)):
                temp = []
                temp.append(float(lat[i]))
                temp.append(float(lon[i]))
                coordinates.append(temp)

                # Add the polygon to the map
            
            polygon = folium.Polygon(locations=coordinates, color="red", fill=True)
            polygon.add_to(m)


            # Store the polygon and its button in the dictionary
            self.polygons[os.path.basename(json_file)] = coordinates

        # Save the map with the global variable
        save_map_with_global_variable(m, "map.html")

        # Create a QWebEngineView, load the HTML file
        
        self.view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))

        # Add the QWebEngineView to the mapPage
        self.mapPage.layout().addWidget(self.view)

        if len(self.buttons) > 0:
            for button in self.buttons:
                self.rightMenu.layout().removeWidget(button)
                button.deleteLater()
            self.buttons.clear()

        for i in self.polygons:
            # Create a button and set its object name to the key of the polygon
            button = QPushButton(i)
            button.setObjectName(i)
            self.rightMenu.layout().addWidget(button)
            self.buttons.append(button)
        
        for button in self.buttons:
            # Connect the button's clicked signal to the focus_on_polygon method
            button.clicked.connect(lambda _, b=button: self.focus_on_polygon(self.polygons[b.objectName()]))
                      
        # Load the HTML file
        for button in self.buttons:
            button.hide()
        self.view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))
        
        

    def focous_on_the_field(self, centroid):
        # Switch to the field page
        self.mainPages.setCurrentWidget(self.mapPage)
        
        # Load the map.html file into QWebEngineView
        self.view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))
        
        # After the map is fully loaded, center the map on specific coordinates
        self.view.loadFinished.connect(self.center_map_on_coordinates(centroid))

    def center_map_on_coordinates(self, centroid):
        # Replace these coordinates with the ones you want to center on
        lat, lon = 52.283333, 10.4515  # Example coordinates
        
        # Use JavaScript to pan the map to the specified coordinates
        self.view.page().runJavaScript(f"""
            m.setView([{lat}, {lon}], 10);  // Set view to the coordinates with zoom level 10
        """)
    def focus_on_polygon(self, polygon):
            # Get the coordinates of the polygon
            # Calculate the centroid of the polygon
        coordinates = polygon
        centroid = [sum(x) / len(x) for x in zip(*coordinates)]
        print("Centroid: ", type(centroid))
        self.mainPages.setCurrentWidget(self.mapPage)
        
            # Load the map.html file into QWebEngineView
        self.view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))

        lat, lon = 52.283333, 10.4515  # Example coordinates
        print("Centroid: ", centroid)
        
        self.view.loadFinished.connect(lambda _: self.view.page().runJavaScript(f"""
            map.setView([{centroid[0]}, {centroid[1]}], 15);  // Set view to the coordinates with zoom level 10
        """))
            

    def openUrl(self, url):
        QDesktopServices.openUrl(url)   
    
    def fetch_wmes_data(self):
        try:
            response = requests.get('http://127.0.0.1:5000/')  # Replace with your server URL
            if response.status_code == 200:
                wmes = response.json()
                self.populate_table(wmes)
            else:
                print(f"Failed to fetch WMES data. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch WMES data. Error: {e}")

    def fetch_fwmes_data(self):
        try:
            response = requests.get('http://127.0.0.1:5000/fwmes')  # Replace with your server URL
            if response.status_code == 200:
                wmes = response.json()
                self.populate_ftable(wmes)
            else:
                print(f"Failed to fetch WMES data. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch WMES data. Error: {e}")

    def populate_ftable(self, wmes):
        # Assume that the object name of the QTableWidget in your .ui file is "tableWidget"
        
        self.tableWidget_2.setRowCount(len(wmes))
        self.tableWidget_2.setColumnCount(1)

        for row, tup in enumerate(wmes):
            item = QTableWidgetItem(str(tup))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item uneditable
            self.tableWidget_2.setItem(row, 0, item)

        self.tableWidget_2.setColumnWidth(0, 400)
        # Set the size policy of the table widget to expand with the window
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableWidget_2.setSizePolicy(sizePolicy)
        
    
    def populate_table(self, wmes):
        # Assume that the object name of the QTableWidget in your .ui file is "tableWidget"
        
        self.tableWidget.setRowCount(len(wmes))
        self.tableWidget.setColumnCount(1)

        for row, tup in enumerate(wmes):
            item = QTableWidgetItem(str(tup))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make the item uneditable
            self.tableWidget.setItem(row, 0, item)

        self.tableWidget.setColumnWidth(0, 400)

    def on_cellClicked(self, row, column):
            self.explainBtn.show()

            # Calculate the position relative to the table's viewport
            rect = self.tableWidget.visualItemRect(self.tableWidget.item(row, column))
            topLeft = self.tableWidget.viewport().mapToGlobal(rect.topLeft())
            tableTopLeft = self.tableWidget.mapToGlobal(self.tableWidget.pos())

            # Adjust position considering the scrolling offset and possibly add a small offset for fine-tuning
            x_position = self.tableWidget.geometry().right()
            y_position = topLeft.y() - tableTopLeft.y() + self.tableWidget.verticalHeader().sectionSize(0)

            # Fine-tune the y_position by adding an offset
            y_position += 185

            # Move the "Explain" button to the correct position
            self.explainBtn.move(x_position, y_position)
            
            # Disconnect any previously connected slots
            try:
                self.explainBtn.clicked.disconnect()
            except TypeError:
                pass  # No slots were connected

            # Get the content of the clicked cell
            cell_content = self.tableWidget.item(row, column).text()
            self.explainBtn.clicked.connect(lambda: self.explain_clicked(cell_content))



    def explain_clicked(self, row):

    
        response = requests.post('http://127.0.0.1:5000/explain', data={'row': row})

        if response.status_code == 200:
            explanation = response.json()
            explainable_plot.plot_sunburst(row)
            self.show_html_plot("sunburst_plot.html")
        

    def show_html_plot(self, html_file):
        # Path to the saved HTML plot
        html_file = "sunburst_plot.html"

        # Create a new window for displaying the plot
        self.plot_window = QMainWindow()
        self.plot_window.setWindowTitle("Plot Viewer")
        self.plot_window.setGeometry(100, 100, 800, 600)

        # QWebEngineView to display the HTML plot
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(html_file)))

        self.plot_window.setCentralWidget(self.browser)
        self.plot_window.show()

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def init_map(self):


        # Create a label
        self.combo.clear()

        self.combo.addItem("agnw:Areacode")
        self.combo.addItem("agnw:CloverRate")
        self.combo.addItem("agnw:CurrentCrop")
        self.combo.addItem("agnw:EarVisible")
        self.combo.addItem("agnw:FrozenGround")
        self.combo.addItem("agnw:GrassFlowering")
        self.combo.addItem("agnw:GrassHeight")
        self.combo.addItem("agnw:GrowthStageClover")
        self.combo.addItem("agnw:GrowthStageGrass")
        self.combo.addItem("agnw:MaizeCover")
        self.combo.addItem("agnw:MoleHillCount")
        self.combo.addItem("agnw:SnowCovered")
        self.combo.addItem("rdf:type")
        
        self.temp_data = []
         # Add button
        self.add_button.clicked.connect(self.add_attribute_value)


        # Display widget
        self.display_att.setReadOnly(True)

        self.inf_butt.clicked.connect(self.update_database)
        
        self.clear_layout(self.layout_map)
        #self.layout = QVBoxLayout()

        self.label = QLabel('Draw a polygon on the map and get the coordinates')
        self.layout_map.addWidget(self.label)

        self.map_view = QWebEngineView()
        self.layout_map.addWidget(self.map_view)

        self.submit_button = QPushButton('Add coordinates')
        self.submit_button.clicked.connect(self.get_polygon_coordinates)
        self.layout_map.addWidget(self.submit_button)

        self.coordinates_label = QLabel('')
        self.layout_map.addWidget(self.coordinates_label)

        
        #self.map_wid.setLayout(self.layout)
        # self.setCentralWidget(self.map_wid)
        # self.setCentralWidget(self.butt_wid)

        map_ = folium.Map(location=[0, 0], zoom_start=2)

        draw = Draw(export=True)
        draw.add_to(map_)

        data = io.BytesIO()
        map_.save(data, close_file=False)
        map_html = data.getvalue().decode()

        # Add JavaScript to initialize the map variable
        map_html = map_html.replace('<head>', '<head><script>var map;</script>')
        map_html = map_html.replace('L.map(', 'map = L.map(')

        self.map_view.setHtml(map_html)

    @pyqtSlot()
    def update_database(self):
        print('Updating database')
        print(self.temp_data)
        create_field.add_field(self.temp_data, len(self.buttons))
        # Send the data to the server
        self.temp_data = []
        self.display_att.clear()
        thread = threading.Thread(target = self.fetch_wmes_data)
        thread.start()
        self.add_new_field_polygoan()
        self.temp_data = []
        self.display_att.clear()


    @pyqtSlot()
    def add_attribute_value(self):
        
        print('Adding attribute and value')
        attribute = self.combo.currentText()
        value = self.value_input.toPlainText()
        if attribute and value:
            self.temp_data.append((attribute, value))
            self.display_att.append(f'{attribute}: {value}')
            print(f'Added {attribute}: {value}')
            self.value_input.clear()
        else:
            self.display_att.append('Please select an attribute and enter a value.')


    @pyqtSlot()
    def get_polygon_coordinates(self):
        self.map_view.page().runJavaScript(
            """
            var coords = [];
            map.eachLayer(function (layer) {
                if (layer instanceof L.Polygon) {
                    coords.push(layer.getLatLngs());
                }
            });
            coords;
            """,
            self.extract_coordinates
        )

    def extract_coordinates(self, result):
        if result:
            coordinates = result[0][0]  
            coordinates_str = '\n'.join([f"({lat}, {lng})" for lat, lng in coordinates])
            self.coordinates_label.setText(f'Polygon Coordinates:\n{coordinates_str}')
            print("Polygon Coordinates:")
            print(coordinates)
            self.temp_data.append(('coordinates', coordinates))
            self.display_att.append(f'coordinates: {coordinates}')
        else:
            self.coordinates_label.setText('No Polygon found')
            print('No Polygon found')
 
    def on_click(self):
        directory = os.path.join(os.getcwd(), 'db')
        if directory:
            self.current_directory = directory
            self.list_files(directory)

    def list_files(self, directory):
        self.listWidget.clear()
        for file_name in os.listdir(directory):
            self.listWidget.addItem(file_name)

    def edit_file(self):
        selected_file = self.listWidget.currentItem().text()
        with open(os.path.join(self.current_directory, selected_file), 'r') as file:
            content = file.read()
        self.textEdit.setText(content)

    def save_file(self):
        selected_file = self.listWidget.currentItem().text()
        edited_content = self.textEdit.toPlainText()
        with open(os.path.join(self.current_directory, selected_file), 'w') as file:
            file.write(edited_content)
        thread1 = threading.Thread(target = self.fetch_wmes_data)
        thread1.start()

    def go_to_map(self):
        
        # Switch to the second page
        self.mainPages.setCurrentWidget(self.mapPage)
        for button in self.buttons:
            button.show()

    def go_to_specific_field(self):
    # Switch to the field page
        self.mainPages.setCurrentWidget(self.fieldPage)

        
        # Load the map.html file into QWebEngineView
        self.view.load(QUrl.fromLocalFile(os.path.abspath("map.html")))
        
        # After the map is fully loaded, center the map on specific coordinates
        self.view.loadFinished.connect(self.center_map_on_coordinates)

    def center_map_on_coordinates(self):
        # Replace these coordinates with the ones you want to center on
        lat, lon = 52.283333, 10.4515  # Example coordinates
        
        # Use JavaScript to pan the map to the specified coordinates
        self.view.page().runJavaScript(f"""
            map.setView([{lat}, {lon}], 10);  // Set view to the coordinates with zoom level 10
        """)


    def go_to_field(self):
        
        # Switch to the second page
        self.mainPages.setCurrentWidget(self.fieldPage)
        for button in self.buttons:
            button.hide()
        self.init_map()
    def go_to_fwmes(self):
        
        # Switch to the second page
        self.mainPages.setCurrentWidget(self.fWmesPage)
        self.fetch_fwmes_data()
        for button in self.buttons:
            button.hide()

    def go_to_home(self):

        # Switch to the second page
        self.mainPages.setCurrentWidget(self.homePage)
        for button in self.buttons:
            button.hide()
        
    
    def go_to_about(self):
        # self.timer.stop()
        # Switch to the second page
        self.mainPages.setCurrentWidget(self.aboutPage)
        for button in self.buttons:
            button.hide()

    def go_to_settings(self):
        
        # Switch to the second page
        self.on_click()
        self.editButton.clicked.connect(self.edit_file)
        self.saveButton.clicked.connect(self.save_file)
        self.mainPages.setCurrentWidget(self.settingsPage)
        for button in self.buttons:
            button.hide()

    def toggle_left_menu(self):
    # Check if the left menu is visible
        if self.leftMenu.isVisible():
            # If it's visible, hide it
            self.leftMenu.hide()
        else:
            # If it's not visible, show it
            self.leftMenu.show()
    
        
    def animate_button(self):
        # Remove the icon
        self.menuBtn.setIcon(QIcon())

        # Start a QTimer to 
        # reapply the icon after a second
        QTimer.singleShot(100, self.reapply_icon)

    def reapply_icon(self):
        # Reapply the icon
        self.menuBtn.setIcon(QIcon("QSS/Icons/d33.png"))

    def button_clicked(self, button):
        # Reset the style of all buttons
        
        self.mapBtn.setStyleSheet("")
        self.homeBtn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border-left: 4px solid transparent;
                }
        """)
        self.aboutBtn.setStyleSheet("")
        self.settingsBtn.setStyleSheet("")
        self.fieldBtn.setStyleSheet("")
        self.fWmes.setStyleSheet("")
        
        self.explainBtn.hide()

        # Change the style of the clicked button
        button.setStyleSheet("""
            QPushButton {
                background-color: black;
                border-left: 4px solid green; 
            }
        """)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())