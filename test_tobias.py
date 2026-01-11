# Modules
import os # for: list files
import time # for: _get_time_HH_MM_SS_mmm

class Logger:
    MAX_LOG_TYPE_LEN = 7
    # a line will look like that
    # [00:00:15.750] [INFO]		System Started
    # [00:00:17.750] [ERROR]	System Crashed
    # [00:00:17.750] [WARNING]	System Almost Crashed :)
    
    def __init__(self):
        """
        Here is the "init" function, it will be executed a the starting of the program
        (When the class is initialised)
        Here will be all the setup things.
        """
        
        # Check actual log file number
        logs_files_list = os.listdir("logs_files")
        
        self.log_file_number = len(logs_files_list)
        self.log_file_path = f"logs_files/log_{self.log_file_number}.txt"
        
        # Create the file (and add a section)
        with open(self.log_file_path, "w") as f:
            f.write("=== LOGS STARTED (v0.1) ===\n")
        
        self.file = open(self.log_file_path, "a")
        
    def _get_time_HH_MM_SS_mmm(self, bias_ms: int = 0):
        """
        Backend Function, do not use it!
        Return timestamp like this: HH:MM:SS.mmm
        Uses time.ticks_ms() for actual millisecond precision.
        """
        import time
        from machine import RTC

        # 1. Get the wall-clock time from RTC
        rtc = RTC()
        dt = rtc.datetime()
        hours, minutes, seconds = dt[4], dt[5], dt[6]

        # 2. Get high-resolution milliseconds
        # time.ticks_ms() returns total ms since boot. 
        # Taking modulo 1000 gives us the ms within the current second.
        milliseconds = time.ticks_ms() % 1000

        # 3. Return the time with padded zeros
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def _add_line(self, line_type:str, details:str, time_bias: int = 0):
        """
        Backend Function to add a line, do not use it !
        Add a line for logging (see format in comment at the start of the class)
        time_bias: idk to explain
        line_type: example: DEBUG, INFO, ...
        details: see format
        """
        # Setup of the time
        actual_time = self._get_time_HH_MM_SS_mmm(time_bias)
        final_string = f"[{actual_time}]  "
        
        # Type part
        type_string = f"[{line_type.upper().strip()}]"
        type_string += (self.MAX_LOG_TYPE_LEN - len(type_string) + 4) * " "
        
        final_string += type_string
        
        # The last thing: the details
        final_string += details.strip()
        
        # Finaly, we write it
        self.file.write(f"{final_string}\n")
        """
        with open(self.log_file_path, "a") as f:
            f.write(f"{final_string}\n")"""
    
    def force_saving(self):
        """
        Force the saving of the logs
        """
        self.file.close()
        self.file = open(self.log_file_path, "a")
        
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
# Note: this will not be executed if the class is ONLY imported
if __name__ == "__main__":
    logger = Logger()
    
    for i in range(100):
        logger.add_info_line("some text and " + str(i))
    
    logger.force_saving()
