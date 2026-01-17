class BinaryLogger:
    TIME_PLAN = [
        ("year", [12, 0, 4095]),
        ("month", [4, 1, 12]),
        ("day", [5, 1, 31]),
        ("hour", [5, 0, 23]),
        ("minute", [6, 0, 59]),
        ("second", [6, 0, 59]),
        ("milisecond", [10, 0, 999])
    ]
    
    SENSORS = [
        ("system", [(8, "int", 0, 255)]),                                                 # 0 : System State
        ("temperature", [(16, "int^1", 0, 1000)]),                                        # 1 : Temperature
        ("pressure", [(16, "int^2", 850_00, 1050_00)]),                                   # 2 : Pressure
        ("Humidity", [(16, "int^1", 0, 1000)]),                                           # 3 : Humidity
        ("Altitude", [(16, "int", 0, 10_000)]),                                           # 4 : Altitude
        ("Acc", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),   # 5 : Acc (3)
        ("Gyro", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),  # 6 : Gyro (3)
        ("Mag", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),   # 7 : Mag (3)
    ]
    
    def __init__(self, file_name="log.bin", erase_file=True):
        self.filename = file_name
        
        if erase_file:
            with open(self.filename, 'wb') as f:
                f.write(b'')
                
    def start_logging(self, year, month, day, hour, minute, second, milisecond):
        self.last_time = (hour*3600 + minute * 60 + second) * 1000 + milisecond  ### ERROR AFTER MIDNIGHT
        
        with open(self.filename, 'ab') as f:
            packed = self.pack_datetime(year, month, day, hour, minute, second, milisecond)
            f.write(packed)
            
    def log_sensor(self, id, values, hour, minute, second, milisecond):
        delta = (hour*3600 + minute * 60 + second) * 1000 + milisecond - self.last_time
                
        self.last_time += delta
        
        delta_s = int(delta/1000)
        delta_m = delta - delta_s * 1000
        
        with open(self.filename, 'ab') as f:
            packed = self.make_log_line(id, values, delta_s, delta_m)
            f.write(packed)
        
    def pack_data(self, plan: list, data: dict) -> bytes:
        ### PLAN + DATA ==> BYTES
        
        pack = 0
        bit_position = 0
        
        for name, field_info in plan:  
            bits, min_val, max_val = field_info
            
            # Get value
            value = data.get(name)
            if value is None:
                raise ValueError(f"Where is the data ?: {name}")
            
            # Check value
            if not (min_val <= value <= max_val):
                raise ValueError(f"Value {name}={value} too large [{min_val}-{max_val}]")
            value -= min_val
            # Mask
            mask = (1 << bits) - 1
            
            # Let's do it
            pack <<= bits
            pack |= (value & mask)  
            
            bit_position += bits
        
        # Count bytes
        total_bits = bit_position
        num_bytes = (total_bits + 7) // 8
        
        # Convert to bytes (big)
        return pack.to_bytes(num_bytes, 'big')
    
    def pack_datetime(self, year, month, day, hour, minute, second, milisecond) -> bytes:
        ### PACK FULL TIME
        data = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "milisecond": milisecond
        }
        return self.pack_data(self.TIME_PLAN, data)
    
    def get_sensor_data_plan(self, id):
        plan = [
            ("id", [8, 0, 255]), 
            ("second", [6, 0, 59]),
            ("mili", [10, 0, 999])
        ]
        i = 0
        for dt in self.SENSORS[id][1]:
            bytes_count = (dt[0] + 7) // 8
            v_min = dt[2]
            v_max = dt[3]
            
            plan.append(("#" + str(i), [bytes_count*8, v_min, v_max]))
            i += 1
        
        return plan
                
    def make_log_line(self, id, values: list, delta_sec, delta_mili):
        plan = [
            ("id", [8, 0, 255]), 
            ("second", [6, 0, 59]),
            ("mili", [10, 0, 999])
        ]
        data = {
            "id": id,
            "second": delta_sec,
            "mili": delta_mili
        }
        
        i = 0
        for dt in self.SENSORS[id][1]:
            bytes_count = (dt[0] + 7) // 8
            v_type = dt[1]
            v_min = dt[2]
            v_max = dt[3]
            
            value = values[i]
            
            if v_type != "int":
                if v_type[0:3] == "int^":
                    k = 10**(int(v_type.split("^")[1]))
                    value = value * k
            
            plan.append(("#" + str(i), [bytes_count*8, v_min, v_max]))
            data["#" + str(i)] = value
            
            i += 1
            
        return self.pack_data(plan, data) 
    
    def unpack_data(self, plan: list, packed_bytes: bytes) -> dict:
        ### BUCKET OF BYTES + PLAN ==> DATA
        
        # Convert data
        packed_int = int.from_bytes(packed_bytes, 'big')
        
        result = {}
        
        total_bits = sum(info[0] for _, info in plan)  
        
        remaining = packed_int
        
        for name, field_info in reversed(plan):  
            bits, min_val, max_val = field_info
            
            # Mask
            mask = (1 << bits) - 1
            
            # Extract value
            value = remaining & mask
            value += min_val
            result[name] = value
            
            # I like to move it it
            remaining >>= bits
        
        ordered_result = {}
        for name, _ in plan: 
            ordered_result[name] = result[name]
        
        return ordered_result
    
    def print_file_content(self):
        try:
            with open(self.filename, 'rb') as f:
                content = f.read()
            
            if not content:
                print(f"'{self.filename}' is empty.")
                return
            
            print(f"=== Content of '{self.filename}' ===")
            print(f"Size: {len(content)} bytes")
            print(f"\nSoup:")
            print(content.hex())
            
            return content
        except OSError:
            print(f"'{self.filename}' doesn't exist")

if __name__ == "main":
    # test
    logger = BinaryLogger()

    logger.start_logging(
        2026,
        1,
        17,
        12,
        15,
        15,
        500
    )

    logger.log_sensor(0, [42], 12, 16, 10, 400)

    packed = logger.print_file_content()

    timestamp_bytes = packed[:6]
    decoded_time = logger.unpack_data(logger.TIME_PLAN, timestamp_bytes)
    sensors_data = packed[6:]
    print(sensors_data.hex())
    print(logger.unpack_data(logger.get_sensor_data_plan(0), sensors_data))
    print("\nTimestamp décodé:")
    print(decoded_time)

class BinaryLogger:
    TIME_PLAN = [
        ("year", [12, 0, 4095]),
        ("month", [4, 1, 12]),
        ("day", [5, 1, 31]),
        ("hour", [5, 0, 23]),
        ("minute", [6, 0, 59]),
        ("second", [6, 0, 59]),
        ("milisecond", [10, 0, 999])
    ]
    
    SENSORS = [
        ("system", [(8, "int", 0, 255)]),                                                 # 0 : System State
        ("temperature", [(16, "int^1", 0, 1000)]),                                        # 1 : Temperature
        ("pressure", [(16, "int^2", 850_00, 1050_00)]),                                   # 2 : Pressure
        ("Humidity", [(16, "int^1", 0, 1000)]),                                           # 3 : Humidity
        ("Altitude", [(16, "int", 0, 10_000)]),                                           # 4 : Altitude
        ("Acc", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),   # 5 : Acc (3)
        ("Gyro", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),  # 6 : Gyro (3)
        ("Mag", [(8, "int", -127, 127), (8, "int", -127, 127), (8, "int", -127, 127)]),   # 7 : Mag (3)
    ]
    
    def __init__(self, file_name="log.bin", erase_file=True):
        self.filename = file_name
        
        if erase_file:
            with open(self.filename, 'wb') as f:
                f.write(b'')
                
    def start_logging(self, year, month, day, hour, minute, second, milisecond):
        self.last_time = (hour*3600 + minute * 60 + second) * 1000 + milisecond  ### ERROR AFTER MIDNIGHT
        
        with open(self.filename, 'ab') as f:
            packed = self.pack_datetime(year, month, day, hour, minute, second, milisecond)
            f.write(packed)
            
    def log_sensor(self, id, values, hour, minute, second, milisecond):
        delta = (hour*3600 + minute * 60 + second) * 1000 + milisecond - self.last_time
                
        self.last_time += delta
        
        delta_s = int(delta/1000)
        delta_m = delta - delta_s * 1000
        
        with open(self.filename, 'ab') as f:
            packed = self.make_log_line(id, values, delta_s, delta_m)
            f.write(packed)
        
    def pack_data(self, plan: list, data: dict) -> bytes:
        ### PLAN + DATA ==> BYTES
        
        pack = 0
        bit_position = 0
        
        for name, field_info in plan:  
            bits, min_val, max_val = field_info
            
            # Get value
            value = data.get(name)
            if value is None:
                raise ValueError(f"Where is the data ?: {name}")
            
            # Check value
            if not (min_val <= value <= max_val):
                raise ValueError(f"Value {name}={value} too large [{min_val}-{max_val}]")
            value -= min_val
            # Mask
            mask = (1 << bits) - 1
            
            # Let's do it
            pack <<= bits
            pack |= (value & mask)  
            
            bit_position += bits
        
        # Count bytes
        total_bits = bit_position
        num_bytes = (total_bits + 7) // 8
        
        # Convert to bytes (big)
        return pack.to_bytes(num_bytes, 'big')
    
    def pack_datetime(self, year, month, day, hour, minute, second, milisecond) -> bytes:
        ### PACK FULL TIME
        data = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second,
            "milisecond": milisecond
        }
        return self.pack_data(self.TIME_PLAN, data)
    
    def get_sensor_data_plan(self, id):
        plan = [
            ("id", [8, 0, 255]), 
            ("second", [6, 0, 59]),
            ("mili", [10, 0, 999])
        ]
        i = 0
        for dt in self.SENSORS[id][1]:
            bytes_count = (dt[0] + 7) // 8
            v_min = dt[2]
            v_max = dt[3]
            
            plan.append(("#" + str(i), [bytes_count*8, v_min, v_max]))
            i += 1
        
        return plan
                
    def make_log_line(self, id, values: list, delta_sec, delta_mili):
        plan = [
            ("id", [8, 0, 255]), 
            ("second", [6, 0, 59]),
            ("mili", [10, 0, 999])
        ]
        data = {
            "id": id,
            "second": delta_sec,
            "mili": delta_mili
        }
        
        i = 0
        for dt in self.SENSORS[id][1]:
            bytes_count = (dt[0] + 7) // 8
            v_type = dt[1]
            v_min = dt[2]
            v_max = dt[3]
            
            value = values[i]
            
            if v_type != "int":
                if v_type[0:3] == "int^":
                    k = 10**(int(v_type.split("^")[1]))
                    value = value * k
            
            plan.append(("#" + str(i), [bytes_count*8, v_min, v_max]))
            data["#" + str(i)] = value
            
            i += 1
            
        return self.pack_data(plan, data) 
    
    def unpack_data(self, plan: list, packed_bytes: bytes) -> dict:
        ### BUCKET OF BYTES + PLAN ==> DATA
        
        # Convert data
        packed_int = int.from_bytes(packed_bytes, 'big')
        
        result = {}
        
        total_bits = sum(info[0] for _, info in plan)  
        
        remaining = packed_int
        
        for name, field_info in reversed(plan):  
            bits, min_val, max_val = field_info
            
            # Mask
            mask = (1 << bits) - 1
            
            # Extract value
            value = remaining & mask
            value += min_val
            result[name] = value
            
            # I like to move it it
            remaining >>= bits
        
        ordered_result = {}
        for name, _ in plan: 
            ordered_result[name] = result[name]
        
        return ordered_result
    
    def print_file_content(self):
        try:
            with open(self.filename, 'rb') as f:
                content = f.read()
            
            if not content:
                print(f"'{self.filename}' is empty.")
                return
            
            print(f"=== Content of '{self.filename}' ===")
            print(f"Size: {len(content)} bytes")
            print(f"\nSoup:")
            print(content.hex())
            
            return content
        except OSError:
            print(f"'{self.filename}' doesn't exist")

if __name__ == "main":
    # test
    logger = BinaryLogger()

    logger.start_logging(
        2026,
        1,
        17,
        12,
        15,
        15,
        500
    )

    logger.log_sensor(0, [42], 12, 16, 10, 400)

    packed = logger.print_file_content()

    timestamp_bytes = packed[:6]
    decoded_time = logger.unpack_data(logger.TIME_PLAN, timestamp_bytes)
    sensors_data = packed[6:]
    print(sensors_data.hex())
    print(logger.unpack_data(logger.get_sensor_data_plan(0), sensors_data))
    print("\nTimestamp décodé:")
    print(decoded_time)

