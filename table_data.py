from functions import BASE_WIDTH, BASE_HEIGHT, NUMBERS, TRIGON_FUNCS, outer_split

class Cell:

    def __init__(self, data: str = "") -> None:
        self.data: str | float = data
        self.text = self.data
        self.base_text = self.data
        self.table = None
        if data != "":
            self.update()

    def update(self) -> float|str|None:
        self.text = self.data
        def update_when_equ():
            if self.text[0] == "=":
                func = self.__compile()
                if isinstance(func, str) and func[0] == "=":
                    self.text = func
                    return update_when_equ()
                return func
        if len(self.text) == 0:
            return ""
        if self.text[0] == "=":
            return update_when_equ()
        for x in self.data:
            if x not in "1234567890.,e-":
                return
        self.data = float(self.data)
        return self.data

    def __compile(self) -> float|str:
        # Recreates string into list with list[indices] or strings or returns value if Function is inside
        text = self.text[1:]

        text += " "
        text_list = []
        numbers = []

        if "(" in text:
            text = text.replace(" ", "")
            ind1 = text.index("(")
            func = text[:ind1]
            ind2 = -(text[::-1].index(")")+1)
            text_to_split = text[ind1+1:ind2]
            if func == "IF":
                splitted_text = outer_split(text_to_split, ",")
                return FUNCS[func](self, splitted_text[0], splitted_text[1], splitted_text[2])
            elif func in TRIGON_FUNCS:
                self.data = text_to_split
                val = self.update()
                self.data = val
                self.calc()
                return TRIGON_FUNCS[func](self.data)
            elif func == "ROUND":
                # DOKONCIT
                pass

        for i in range(len(text)):
            if text[i] == "|":
                temp = []
                for x in reversed(range(len(text[:i]))):
                    if text[x] not in NUMBERS:
                        temp.append(x+1)
                        break
                if len(temp) == 0:
                    temp.append(0)
                for y in range(i+1, len(text)):
                    if text[y] not in NUMBERS:
                        temp.append(y)
                        break
                numbers.append(temp)
        
        if len(numbers) == 0:
            return eval(text)
        
        tt = [text[x[0]:x[1]] for x in numbers]
        temp_list = [[int(x) for x in t.split("|")] for t in tt]
        
        text_list.append(text[:numbers[0][0]])
        text_list.append(temp_list[0])
        
        for i in range(len(numbers)-1):
            text_list.append(text[numbers[i][1]:numbers[i+1][0]])
            text_list.append(temp_list[i+1])
            
        text_list.append(text[numbers[-1][1]:])
        
        self.data = text_list.copy()
        return self.data

    def __repr__(self) -> str:
        return str(self.data)
    
    def calc(self) -> None:
        # Calculates cell's value if = is in string with index 0
        cell = self.data
        if type(cell) == float or type(cell) == int:
            return
        text_to_calc = ""
        for x in cell:
            if type(x) == list:
                d = self.table[x[0]-1][x[1]-1].data
                if d == '':
                    d = 0
                text_to_calc += str(d)
            else:
                text_to_calc += x
        result = eval(text_to_calc)
        self.data = result


class Table:
    
    def __init__(self) -> None:
        self.table: list[list[Cell]] = []
        self.full_data: dict[tuple[int, int], tuple[str, str]] = dict()
        self.width = BASE_WIDTH
        self.height = BASE_HEIGHT
        for h in range(self.height):
            l = []
            for w in range(self.width):
                c = Cell()
                c.table = self
                l.append(c)
            self.table.append(l)
            
    def __getitem__(self, index1) -> list[Cell]:
        self.scale_table(index1, self.width-1)
        return self.table[index1]
    
    def setitem(self, index1: int, index2: int, item) -> None:
        self.scale_table(index1, index2)
        self.table[index1][index2].base_text = item
        self.table[index1][index2].data = item
        f = self.table[index1][index2].update()
        if isinstance(f, list):
            f = self.calc(index1, index2)
        if f is not None:
            self.table[index1][index2].data = f
        self.full_data[(index1, index2)] = (item, f)
        
    def __len__(self) -> int:
        return len(self.table)
    
    def scale_table(self, index1: int, index2: int) -> None:
        # Scales table to width and height
        if index2 > self.width - 1:
            num_range = (index2+1) - self.width
            for x in range(num_range):
                self.add_width()
        if index1 > self.height - 1:
            num_range = (index1+1) - self.height
            for x in range(num_range):
                self.add_height()
                
    def add_width(self) -> None:
        self.width += 1
        for h in self.table:
            c = Cell()
            c.table = self
            h.append(c)
            
    def add_height(self) -> None:
        self.height += 1
        v = []
        for _ in range(self.width):
            c = Cell()
            c.table = self
            v.append(c)
        self.table.append(v)
        
    def view_item(self, index1: int, index2: int) -> int |float| str:
        # Returns data of cell
        self.scale_table(index1, index2)
        return self.__getitem__(index1, index2)
    
    def sum(self, i1: int, i2: int, j1: int, j2: int) -> float:
        # Returns sum of table with following indices in argument
        result = 0.0
        for row in range(i1, j1+1):
            for col in range(i2, j2+1):
                if type(self.table[row][col].data) not in (float, int):
                    raise Exception("You cannot add other types then numbers")
                result += self.table[row][col].data
        return result

    def calc(self, i1: int, i2: int) -> float:
        # Calculates cell's value if = is in string with index 0
        cell = self.table[i1][i2].data
        if type(cell) == float or type(cell) == int:
            return
        text_to_calc = ""
        for x in cell:
            if type(x) == list:
                d = self.table[x[0]-1][x[1]-1].data if x[0] - 1 < self.height and x[1] - 1 < self.width else 0
                if d == '':
                    d = 0
                text_to_calc += str(d)
            else:
                text_to_calc += x
        result = eval(text_to_calc)
        self.table[i1][i2].data = result
        return result

    def if_condition(self, condition: str, true_value, false_value) -> int |float| str:
        _count = 0
        for z in ("<", ">", "=="):
            if z in condition:
                _count += 1
        if _count == 0:
            raise Exception("Wrong Input, not condition")
        value = eval(condition) # True | False

        if value:
            return true_value
        else:
            return false_value


FUNCS = {"IF":Table.if_condition}


def save_curr_data_to_csv(file_name: str, table: Table) -> None:
    from csv import writer as csv_write
    data: list[list[str]] = []

    for row in table.table:
        temp: list[str] = []
        for cell in row:
            temp.append(str(cell.data))
        data.append(temp)
    
    with open(file_name, "w", newline="") as f:
        writer = csv_write(f, delimiter=";")
        writer.writerows(data)


def save_text_data_to_csv(file_name: str, table: Table) -> None:
    from csv import writer as csv_write
    data: list[list[str]] = []

    for row in table.table:
        temp: list[str] = []
        for cell in row:
            temp.append(cell.base_text)
        data.append(temp)
    
    with open(file_name, "w", newline="") as f:
        writer = csv_write(f, delimiter=";")
        writer.writerows(data)


def transfer_csv_to_table(file_name: str) -> Table:
    from csv import reader as csv_reader

    table = Table()

    with open(file_name, "r") as file:
        reader = list(csv_reader(file, delimiter=";"))

    for y, row in enumerate(reader):
        for x, data in enumerate(row):
            if data != '':
                table.setitem(y, x, data)

    return table


def save_full_data(file_name: str, table: Table) -> None:
    from csv import writer as csv_writer
    data_list: list[tuple] = [("Y", "X", "TEXT", "DATA")]

    for (y, x), (text, data) in table.full_data.items():
        data_list.append((y, x, text, data))
    
    with open(f"{file_name}.csv", "w", newline="") as file:
        writer = csv_writer(file, delimiter=";")
        writer.writerows(data_list)


def csv_full_data_to_table(file_name: str) -> Table:
    from csv import reader as csv_reader

    new_table = Table()

    with open(file_name, "r") as file:
        reader = list(csv_reader(file, delimiter=";"))

    for i in range(1, len(reader)):
        y, x, text, data = reader[i]
        new_table.setitem(int(y), int(x), text)
    
    return new_table
