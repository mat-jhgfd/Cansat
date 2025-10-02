# NOTE: This code is intented to test the protocol with virtual failures. It is badly made but is only to get the point.

import os
import hashlib
import random
import argparse
import time

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# NOTE: This is cool because you can change the values by typing the command with arguments
# example:
# python3 protocol.py --loss 0.2 --corrupt 0.05 --delay 0.1
parser = argparse.ArgumentParser()
parser.add_argument("--loss", type=float, default=0.1, help="Probability of packet loss (0-1)")
parser.add_argument("--corrupt", type=float, default=0.1, help="Probability of packet corruption (0-1)")
parser.add_argument("--delay", type=float, default=0.3, help="Artificial delay between actions (seconds)")
args = parser.parse_args()

LOSS_PROB = args.loss
CORRUPT_PROB = args.corrupt
DELAY = args.delay

# WARNING: It is text for now but should be video later
file_to_test = "./testFile.txt"

# WARNING: This should be 'frames' but i dont want to decompose video into frame rn
lines = []
exchange_log = []

# I just need default bc i get error if i dont :(
sending = False
someoneIsListening = False
connectionStatusConnected = False

# Can be controled with the ArgumentParser
def pause():
    time.sleep(DELAY)


def check_signal():
    global sending
    print(f"hey, is there someone there? I'm {os.getpid()}s sending") # the pid in this case is dumb and not needed. you have to imagine this as a signal that is not long and as a indentifier probably
    sending = True
    pause()
    print()


def i_am_here():
    global someoneIsListening
    print("I'm listening")
    if sending:
        print(f"I get you, I'm {os.getpid()}l listening") # same here
        someoneIsListening = True
    pause()
    print()


def load_file():
    with open(file_to_test, "r") as f:
        for line in f:
            lines.append(line.strip())


def calculate_hash(packet):
    return hashlib.sha256(packet.encode()).hexdigest()


def corrupt_packet(packet):
    if random.random() < CORRUPT_PROB and packet:
        i = random.randint(0, len(packet) - 1)
        packet = list(packet)
        packet[i] = chr(random.randint(32, 126))
        return ''.join(packet)
    return packet


def maybe_drop_packet(packet):
    return None if random.random() < LOSS_PROB else packet


def send_packet(packet, name):
    print(f"[{name}] -> [SEND]")
    pause()

    received = maybe_drop_packet(packet)
    if received is None:
        print(f"[{name}] -> {RED}[NOT RECEIVED]{RESET}")
        print(f"[{name}] -> {RED}[STATUS: BAD] (Packet never arrived){RESET}")
        exchange_log.append({"packet": packet, "packet_name": name, "status": "BAD", "error": "Packet never arrived."})
        pause()
        print()
        return

    print(f"[{name}] -> [RECEIVED]")
    pause()

    received = corrupt_packet(received)

    print(f"[{name}] -> [VERIFICATION]")
    pause()

    if calculate_hash(packet) == calculate_hash(received):
        print(f"[{name}] -> {GREEN}[STATUS: OK]{RESET}")
        exchange_log.append({"packet": packet, "packet_name": name, "status": "OK"})
    else:
        print(f"[{name}] -> {RED}[VERIFICATION FAILED]{RESET}")
        print(f"[{name}] -> {RED}[STATUS: BAD] (Hash mismatch){RESET}")
        exchange_log.append({"packet": packet, "packet_name": name, "status": "BAD", "error": "Hash mismatch"})
    pause()
    print()


def data_exchange():
    print("********************* BEGIN OF EXCHANGE ********************")
    for i, packet in enumerate(lines, 1):
        send_packet(packet, f"Packet {i}")
    print("********************* END OF EXCHANGE ********************")


# the format of this code left me confused like never before
# i got lost between names a bit
def print_bad_log():
    bad = [e for e in exchange_log if e["status"] == "BAD"]
    if bad:
        print("\nBad Packets Log:")
        for e in bad:
            print(f"{RED}{e['packet_name']}: {e['error']}{RESET}")
    else:
        print(f"{GREEN}No bad packets.{RESET}")
    pause()


def resend_failed_packets():
    attempt = 1
    while True:
        bad = [(e["packet"], e["packet_name"]) for e in exchange_log if e["status"] == "BAD"]
        if not bad:
            break

        print(f"\n********************* RESENDING FAILED PACKETS #{attempt} ********************")
        exchange_log[:] = [e for e in exchange_log if e["status"] != "BAD"]

        for packet, name in bad:
            send_packet(packet, name)

        print(f"********************* END OF RETRY #{attempt} ********************")
        print_bad_log()
        attempt += 1


load_file()
check_signal()
i_am_here()

if someoneIsListening:
    print("yay! you are listening")
    print("let's begin the exchange")
    connectionStatusConnected = True
    print()

if connectionStatusConnected:
    while True:
        confirm = input("Do you want to begin the exchange? (y/n): ").strip().lower()
        if confirm in ("y", "n"):
            break
        print(f"{RED}Invalid input. Please enter 'y' or 'n'.{RESET}")

    if confirm == "y":
        data_exchange()
        print_bad_log()
        resend_failed_packets()
    else:
        print("Exchange canceled by user.")
