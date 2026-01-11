# Modules
import os # for: list files
import time # for: _get_time_HH_MM_SS_mmm
from machine import RTC # for: _get_time_HH_MM_SS_mmm

class Logger:
    MAX_LOG_TYPE_LEN = 7  # (Const) : maximum len of a log type. Example: W-A-R-N-I-N-G --> 7 letters
    MAX_LINES = 100  # (Const) : maximum lines in a single file. After that, it will create a new file (see _make_new_file & _add_line)
    
    # a line will look like that:
    # [00:00:15.750] [INFO]		System Started
    # [00:00:17.750] [ERROR]	System Crashed
    # [00:00:17.750] [WARNING]	System Almost Crashed :)
    
    def __init__(self):
        """
        Here is the "init" function, it will be executed a the starting of the program
        (When the class is initialised)
        Here will be all the setup things.
        """

        # Init classes
        self.rtc = RTC()  # Init RTC (for the GPS's time)
                
        # Check actual log folder number & make new dir
        logs_files_list = os.listdir("logs_files")
        
        self.log_file_number = 0
        
        log_folder_number = len(logs_files_list)
        
        os.mkdir(f"logs_files/logs #{log_folder_number}")
        
        self.log_file_base_path = f"logs_files/logs #{log_folder_number}/log_"  # Define the base path. The final path will be: BASE_PATH + N_log + .txt

        # Make the first log file
        self._make_new_file()

    
    def _make_new_file(self):
        """
        Backend Function, do not use it !
        Make a new log file.
        """
        
        # Create the file (and add a section)
        self.log_file_number += 1
        self.log_file_path = self.log_file_base_path + str(self.log_file_number) + ".txt"
        
        with open(self.log_file_path, "w") as f:
            f.write("=== LOGS STARTED (v0.2) ===\n")
        
        self.file = open(self.log_file_path, "a")
        
        self.line_count = 0  # Reset the line count

    
    def _get_time_HH_MM_SS_mmm(self):
        """
        Backend Function, do not use it!
        Return timestamp like this: HH:MM:SS.mmm
        Uses time.ticks_ms() for actual millisecond precision.
        """       

        # 1. Get the wall-clock time from RTC
        dt = self.rtc.datetime()
        hours, minutes, seconds = dt[4], dt[5], dt[6]

        # 2. Get high-resolution milliseconds
        # time.ticks_ms() returns total ms since boot. 
        # Taking modulo 1000 gives us the ms within the current second.
        milliseconds = time.ticks_ms() % 1000

        # 3. Return the time with padded zeros
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    
    def _add_line(self, line_type:str, details:str):
        """
        Backend Function to add a line, do not use it !
        Add a line for logging (see format in comment at the start of the class)
        time_bias: idk to explain
        line_type: example: DEBUG, INFO, ...
        details: see format
        """
        
        self.line_count += 1  # Update the line count (for this file)
        
        # Setup of the time
        actual_time = self._get_time_HH_MM_SS_mmm()
        final_string = f"[{actual_time}]  "
        
        # Type part
        type_string = f"[{line_type.upper().strip()}]"
        type_string += (self.MAX_LOG_TYPE_LEN - len(type_string) + 4) * " "
        
        final_string += type_string
        
        # The last thing: the details
        final_string += details.strip()

        # Check if we don't need to make a new file
        if self.line_count >= self.MAX_LINES:
            self.force_saving()  # Save the last one
            self._make_new_file()  # and create a new one
        
        # Finaly, we write it
        self.file.write(f"{final_string}\n")

    
    def force_saving(self):
        """
        Force the saving of the logs
        """
        self.file.close()
        self.file = open(self.log_file_path, "a")  # "a" --> write in the file and don't delete the content

    
    def add_info_line(self, text):
        """
        add an info line like this:
        [01:32:55.970]  [INFO]    details here
        """
        self._add_line("INFO", str(text))

    
    def add_error_line(self, text):
        """
        add an error line like this:
        [01:32:55.970]  [ERROR]   details here
        """
        self._add_line("ERROR", str(text))


# Here a little example
# Note: this will not be executed if the class is ONLY imported.
# It's a stress test for 10 000 lines, and it work :) 
if __name__ == "__main__":
    logger = Logger()
    
    for i in range(10_000):
        logger.add_info_line("some text and " + str(i))
    
    logger.force_saving()


