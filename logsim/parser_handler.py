from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol


class LineTerminalOutput:
    def __init__(self):
        self.line_location = None
        self.line_with_issue = None
        self.arrow = None
        self.message = None

    def __str__(self):
        return f"\n{self.line_location}\n{self.line_with_issue}{self.arrow}\n{self.message}\n"


class FileTerminalOutput:
    def __init__(self):
        self.message = None

    def __str__(self):
        return f"\nFile error: {self.message}\n"


class ParserErrorHandler:
    def __init__(self, names: Names, devices: Devices, network: Network, monitors: Monitors, scanner: Scanner):
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_output_list = []

        # syntax error
        [self.EXPECT_IDENTIFIER, self.EXPECT_INPUT_DEVICE, self.EXPECT_VARIABLE_INPUT_NUMBER,
         self.EXPECT_CLOCK_CYCLE, self.EXPECT_INITIAL_STATE, self.EXPECT_PIN_IN, self.EXPECT_PIN_OUT,
         self.EXPECT_PIN_IN_OR_OUT, self.EXPECT_KEYWORD, self.EXPECT_OPEN_CURLY_BRACKET, self.EXPECT_COMMA,
         self.EXPECT_SEMICOLON, self.EXPECT_COLON, self.EXPECT_FULL_STOP_OR_SEMICOLON, self.EXPECT_FULL_STOP,
         self.EXPECT_ARROW, self.EXPECT_FULL_STOP_OR_ARROW] = names.unique_error_codes(17)

        # semantic error
        [self.MISSING_CLOCK_OR_SWITCH, self.DUPLICATE_KEYWORD, self.WRONG_BLOCK_ORDER, self.MONITOR_NOT_DEFINED
         ] = names.unique_error_codes(4)

    def handle_error(self, error_code: int, symbol: Symbol) -> None:
        print("handling error")
        if symbol.id:  # symbol id is not None, i.e. symbol.type is KEYWORD, NUMBER or NAME
            if symbol.type == Scanner.NUMBER:
                name = symbol.id
            else:
                name = self.names.get_name_string(symbol.id)
        elif symbol.type == Scanner.COMMA:
            name = ","
        elif symbol.type == Scanner.SEMICOLON:
            name = ";"
        elif symbol.type == Scanner.COLON:
            name = ":"
        elif symbol.type == Scanner.FULL_STOP:
            name = "."
        elif symbol.type == Scanner.ARROW:
            name = ">"
        elif symbol.type == Scanner.OPEN_CURLY_BRACKET:
            name = "{"
        elif symbol.type == Scanner.CLOSE_CURLY_BRACKET:
            name = "}"
        elif symbol.type == Scanner.EOF:
            name = ""
        else:
            raise ValueError("Invalid symbol type")
        error_message = self.get_error_message(error_code=error_code, name=name)
        error_output = self.get_line_terminal_output(line=symbol.line, character_in_line=symbol.character_in_line,
                                                         message=error_message)
        self.error_output_list.append(error_output)

    def file_error(self, error_code: int) -> None:
        error_output = FileTerminalOutput()
        error_output.message = self.get_error_message(error_code=error_code)
        self.error_output_list.append(error_output)

    def get_line_terminal_output(self, line: int, character_in_line: int, message: str) -> LineTerminalOutput:
        terminal_output = LineTerminalOutput()

        terminal_output.line_location = f"Line {line + 1}:"
        terminal_output.line_with_issue = self.scanner.file_lines[line]
        terminal_output.arrow = " " * character_in_line + "^"
        terminal_output.message = message

        return terminal_output

    def get_error_message(self, error_code: int, name: str = "") -> str:
        name = "\"" + name + "\""
        if error_code != self.MISSING_CLOCK_OR_SWITCH and not name:
            raise TypeError(f"error_code = {error_code} has 1 required positional argument: 'name'")
        # syntax error
        if error_code == self.EXPECT_IDENTIFIER:
            return f"Found {name}, expected a non-keyword identifier"
        elif error_code == self.EXPECT_INPUT_DEVICE:
            return f"Found {name}, expected 'AND', 'NAND', 'OR', 'NOR', 'XOR' or 'DTYPE'"
        elif error_code == self.EXPECT_VARIABLE_INPUT_NUMBER:
            return f"Found {name}, expected integer between 1 and 16"
        elif error_code == self.EXPECT_CLOCK_CYCLE:
            return f"Found {name}, expected positive integer with no leading zero"
        elif error_code == self.EXPECT_INITIAL_STATE:
            return f"Found {name}, expected 0 or 1"
        elif error_code == self.EXPECT_PIN_IN:
            return f"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET' or 'CLEAR'"
        elif error_code == self.EXPECT_PIN_OUT:
            return f"Found {name}, expected 'Q' or 'QBAR'"
        elif error_code == self.EXPECT_PIN_IN_OR_OUT:  # for ( pinIn | pinOut ) in monitor
            return f"Found {name}, expected 'I1-16', 'DATA', 'CLK', 'SET', 'CLEAR', 'Q' or 'QBAR'"
        elif error_code == self.EXPECT_KEYWORD:
            return f"Found {name}, expected a keyword ('DEVICE', 'CLOCK', 'SWITCH', 'MONITOR' or 'CONNECTION')"
        elif error_code == self.EXPECT_OPEN_CURLY_BRACKET:
            return f"Found {name}, expected '{{'"
        elif error_code == self.EXPECT_COMMA:
            return f"Found {name}, expected ','"
        elif error_code == self.EXPECT_SEMICOLON:
            return f"Found {name}, expected ';'"
        elif error_code == self.EXPECT_COLON:
            return f"Found {name}, expected ':'"
        elif error_code == self.EXPECT_FULL_STOP_OR_SEMICOLON:  # for [ ".", ( pinIn | pinOut ) ], ";" in monitor
            return f"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)"
        elif error_code == self.EXPECT_FULL_STOP:
            return f"Found {name}, expected '.'"
        elif error_code == self.EXPECT_ARROW:
            return f"Found {name}, expected '>'"
        elif error_code == self.EXPECT_FULL_STOP_OR_ARROW:  # for [".", pinOut] , ">" in connection
            return f"Found {name}, expected '.' (if pin has to be defined) or ';' (if pin does not have to be defined)"

        # semantic error
        elif error_code == self.network.PORT_ABSENT:
            return f"Pin {name} does not exist"
        elif error_code == self.network.INPUT_CONNECTED:
            return f"Connection repeatedly assigned to input pin {name}"
        elif False:  # undefined error code now - implement later
            return f"Missing input to pin {name}"
        elif error_code == self.network.DEVICE_ABSENT:
            return f"Identifier {name} is not defined"
        elif error_code == self.devices.DEVICE_PRESENT or error_code == self.monitors.MONITOR_PRESENT:
            return f"Identifier {name} should not be redefined"
        elif error_code == self.MISSING_CLOCK_OR_SWITCH:
            return f"At least one list between 'CLOCK' and 'SWITCH' is needed. neither is found"
        elif error_code == self.DUPLICATE_KEYWORD:
            return f"{name} block should not be redefined"
        elif error_code == self.WRONG_BLOCK_ORDER:
            return f"{name} block order is wrong"
        elif error_code == self.MONITOR_NOT_DEFINED:
            return f"At least one monitor should be defined"
        else:
            raise ValueError(f"Invalid error code '{error_code}'")
