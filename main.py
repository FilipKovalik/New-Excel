from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QFileDialog, QWidget, QTextEdit, QLineEdit, QColorDialog
from PyQt5.QtGui import QFont, QColor, QBrush
from table_data import *
import sys


class ExcelLikeApp(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MyExcel")
        self.setGeometry(0, 0, 1920, 1080)
        self.layout_ = QVBoxLayout()
        self.data_table = Table()
        self.copied_cells: list[list[str]] | None = None

        # Buttons at the top
        self.load_csv_button = QPushButton("Load CSV")
        self.load_csv_button.clicked.connect(self.load_cvs)
        self.layout_.addWidget(self.load_csv_button)

        self.save_csv_button = QPushButton("Save CSV")
        self.save_csv_button.clicked.connect(self.save_cvs)
        self.layout_.addWidget(self.save_csv_button)

        self.change_colour_button = QPushButton("Change Colour Of Cells")
        self.change_colour_button.clicked.connect(self.change_colour)
        self.layout_.addWidget(self.change_colour_button)

        self.paste_button = QPushButton("Paste Cells")
        self.paste_button.clicked.connect(self.paste_cells)
        self.layout_.addWidget(self.paste_button)

        self.copy_cells_button = QPushButton("Copy Data")
        self.copy_cells_button.clicked.connect(self.copy_cells_info)
        self.layout_.addWidget(self.copy_cells_button)

        self.cut_cells_button = QPushButton("Cut Data")
        self.cut_cells_button.clicked.connect(self.cut_cells_info)
        self.layout_.addWidget(self.cut_cells_button)

        # Cell editor
        self.cell_data = QTextEdit(self, plainText="", acceptRichText=False, readOnly=False)
        self.cell_data.setFixedHeight(35)
        self.cell_data.setFont(QFont("Arial", 15))
        self.layout_.addWidget(self.cell_data)

        # Table
        self.table = QTableWidget(40, 40)
        self.table.cellClicked.connect(self.on_cell_click)
        self.table.cellChanged.connect(self.update_data)
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.layout_.addWidget(self.table)

        self.setLayout(self.layout_)
    
    def set_item(self, i1: int, i2: int, item: str) -> None:
        self.scale_table(i1, i2)
        self.data_table.setitem(i1, i2, item)
        self.table.setItem(i1, i2, QTableWidgetItem(str(self.data_table[i1][i2].data)))
    
    def get_item(self, i1: int, i2: int) -> str | None:
        item = self.table.item(i1, i2)
        if item is None:
            return None
        return item.text()
    
    def scale_table(self, index1: int, index2: int) -> None:
        rows = self.table.rowCount()
        cols = self.table.columnCount()

        if index1 > rows - 1:
            self.table.setRowCount(index1 + 1)

        if index2 > cols - 1:
            self.table.setColumnCount(index2 + 1)

    def on_cell_click(self, index1: int, index2: int) -> None:
        self.scale_table(index1, index2)
        self.data_table.scale_table(index1, index2)
        text = self.data_table[index1][index2].base_text
        self.cell_data.setText(text)
    
    def update_data(self, row: int, column: int) -> None:
        item = self.table.item(row, column)
        self.data_table.scale_table(row, column)
        if item.text() == self.data_table[row][column].base_text:
            return
        if item:
            new_value = item.text()
            old_value = str(self.data_table[row][column].data)
            if new_value != old_value:
                self.set_item(row, column, new_value)
    
    def on_double_click(self, row: int, column: int) -> None:
        text = self.data_table[row][column].base_text

        if text != '':
            item = self.table.item(row, column)
            if item is None:
                item = QTableWidgetItem()
                self.table.setItem(row, column, QTableWidgetItem(text))
            item.setText(text)
            editor = self.table.cellWidget(row, column)
            if editor is None:
                editor = QLineEdit(item.text(), self.table)
                editor.textChanged.connect(lambda text: self.on_text_changed(text))
                editor.setFocus()

                editor.returnPressed.connect(lambda: self.on_text_confirm(row, column, editor))
                self.table.setCellWidget(row, column, editor)

    def on_text_changed(self, text) -> None:
        self.cell_data.setText(text)
    
    def on_text_confirm(self, row: int, column: int, editor: QLineEdit) -> None:
        new_text = editor.text()
        self.table.setCellWidget(row, column, None)
        self.set_item(row, column, new_text)

    def push_data_from_table(self, table: Table) -> None:
        for (y, x), (text, data) in table.full_data.items():
            self.set_item(y, x, text)
    
    def load_cvs(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_name:
            table = csv_full_data_to_table(file_name)
            self.push_data_from_table(table)
    
    def save_cvs(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
        if file_name:
            save_full_data(file_name, self.data_table)
    
    def change_colour(self) -> None:
        colour: QColor = QColorDialog.getColor()
        cells = self.table.selectionModel().selectedIndexes()

        for x in cells:
            cell = self.table.item(x.row(), x.column())
            if cell is None:
                self.set_item(x.row(), x.column(), "")
                cell = self.table.item(x.row(), x.column())
            cell.setBackground(QBrush(colour))
    
    def paste_cells(self) -> None:
        if self.copied_cells is None:
            return

        cell = self.table.selectionModel().selectedIndexes()[0]
        row, col = cell.row(), cell.column()
        cell = self.table.item(row, col)

        for y, c in enumerate(self.copied_cells):
            for x, r in enumerate(c):
                self.set_item(y + row, x + col, r)

        self.copied_cells = None

    def copy_cells_info(self) -> None:
        cells = self.table.selectionModel().selectedIndexes()
        self.copied_cells = []

        start_row: int | None = cells[0].row()
        appending_list: list[str] = []
        for c in cells:
            row, col = c.row(), c.column()
            cell = self.table.item(row, col)
            if cell is None:
                self.set_item(row, col, "")
                cell = self.table.item(row, col)
            if row != start_row:
                self.copied_cells.append(appending_list)
                appending_list = []
                start_row = row
            appending_list.append(self.data_table[row][col].base_text)
        
        self.copied_cells.append(appending_list)

    def cut_cells_info(self) -> None:
        self.copy_cells_info()
        cells = self.table.selectionModel().selectedIndexes()

        for cell in cells:
            row, col = cell.row(), cell.column()
            self.set_item(row, col, "")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExcelLikeApp()
    window.show()
    sys.exit(app.exec())
