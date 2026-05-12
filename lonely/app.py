import threading
import jwt
import random
from threading import Thread
import json
import requests 
import google.protobuf
from protobuf_decoder.protobuf_decoder import Parser
import json
import datetime
from datetime import datetime
from google.protobuf.json_format import MessageToJson
import my_message_pb2
import data_pb2
import base64
import logging
import re
import socket
from google.protobuf.timestamp_pb2 import Timestamp
import jwt_generator_pb2
import os
from code_command import handle_code_command
import binascii
import sys
import psutil
from AlliFF import xSendTeamMsg, ArA_CoLor, xBunnEr
import MajorLoginRes_pb2
from time import sleep
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import time
import urllib3
from important_zitado import*
from byte import*  

# حل المشكلة - تعريف threads كقائمة فارغة عالمية
threads = []

def restart_bot():
    print("جارٍ إعادة تشغيل البوت بعد 20 دقيقة...")
    os.execv(sys.executable, ['python'] + sys.argv)

# دالة تشغيل المؤقت في خيط منفصل
def timer_thread():
    while True:
        time.sleep(300)  # 1200 ثانية = 20 دقيقة
        restart_bot()

# بدء المؤقت في خيط منفصل
timer = threading.Thread(target=timer_thread)
timer.daemon = True
timer.start()

tempid = None
sent_inv = False
start_par = False
pleaseaccept = False
nameinv = "none"
idinv = 0
senthi = False
statusinfo = False
tempdata1 = None
tempdata = None
leaveee = False
leaveee1 = False
data22 = None
isroom = False
isroom2 = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def encrypt_packet(plain_text, key, iv):
    plain_text = bytes.fromhex(plain_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()
    
def gethashteam(hexxx):
    a = zitado_get_proto(hexxx)
    if not a:
        raise ValueError("Invalid hex format or empty response from zitado_get_proto")
    data = json.loads(a)
    return data['5']['7']
def getownteam(hexxx):
    a = zitado_get_proto(hexxx)
    if not a:
        raise ValueError("Invalid hex format or empty response from zitado_get_proto")
    data = json.loads(a)
    return data['5']['1']
def get_player_status(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)

    if "5" not in parsed_data or "data" not in parsed_data["5"]:
        return "OFFLINE"

    json_data = parsed_data["5"]["data"]

    if "1" not in json_data or "data" not in json_data["1"]:
        return "OFFLINE"

    data = json_data["1"]["data"]

    if "3" not in data:
        return "OFFLINE"

    status_data = data["3"]

    if "data" not in status_data:
        return "OFFLINE"

    status = status_data["data"]

    if status == 1:
        return "SOLO"
    
    if status == 2:
        if "9" in data and "data" in data["9"]:
            group_count = data["9"]["data"]
            countmax1 = data["10"]["data"]
            countmax = countmax1 + 1
            return f"INSQUAD ({group_count}/{countmax})"

        return "INSQUAD"
    
    if status in [3, 5]:
        return "INGAME"
    if status == 4:
        return "IN ROOM"
    
    if status in [6, 7]:
        return "IN SOCIAL ISLAND MODE .."

    return "NOTFOUND"
def get_idroom_by_idplayer(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]
    data = json_data["1"]["data"]
    idroom = data['15']["data"]
    return idroom
def get_leader(packet):
    json_result = get_available_room(packet)
    parsed_data = json.loads(json_result)
    json_data = parsed_data["5"]["data"]
    data = json_data["1"]["data"]
    leader = data['8']["data"]
    return leader
def generate_random_color():
    color_list = [
        "[00FF00][b][c]",
        "[FFDD00][b][c]",
        "[3813F3][b][c]",
        "[FF0000][b][c]",
        "[0000FF][b][c]",
        "[FFA500][b][c]",
        "[DF07F8][b][c]",
        "[11EAFD][b][c]",
        "[DCE775][b][c]",
        "[A8E6CF][b][c]",
        "[7CB342][b][c]",
        "[FFB300][b][c]",
        "[90EE90][b][c]",
        # الألوان الجديدة المضافة
        "[32CD32][b][c]",
        "[00BFFF][b][c]",
        "[00FA9A][b][c]",
        "[FF4500][b][c]",
        "[FF6347][b][c]",
        "[FF69B4][b][c]",
        "[FF8C00][b][c]",
        "[FFD700][b][c]",
        "[FFDAB9][b][c]",
        "[F0F0F0][b][c]",
        "[F0E68C][b][c]",
        "[D3D3D3][b][c]",
        "[A9A9A9][b][c]",
        "[D2691E][b][c]",
        "[CD853F][b][c]",
        "[BC8F8F][b][c]",
        "[6A5ACD][b][c]",
        "[483D8B][b][c]",
        "[4682B4][b][c]",
        "[9370DB][b][c]",
        "[C71585][b][c]",
        "[FFA07A][b][c]"
    ]
    random_color = random.choice(color_list)
    return random_color
def fix_num(num):
    fixed = ""
    count = 0
    num_str = str(num)  # Convert the number to a string

    for char in num_str:
        if char.isdigit():
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0  
    return fixed


def fix_word(num):
    fixed = ""
    count = 0
    
    for char in num:
        if char:
            count += 1
        fixed += char
        if count == 3:
            fixed += "[c]"
            count = 0  
    return fixed
    
def check_banned_status(player_id):
    url = f"https://chekban-xza.vercel.app/check?uid={player_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {
                    "status": data.get("is_banned", "Unknown"),
                    "player_name": data.get("name", "Unknown"),
                    "ban_period": data.get("ban_period", 0),
                    "region": data.get("region", "Unknown")
                }
            else:
                return {"error": "API request failed"}
        else:
            return {"error": f"Failed to fetch data. Status code: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
def rrrrrrrrrrrrrr(number):
    if isinstance(number, str) and '***' in number:
        return number.replace('***', '106')
    return number
                
def Encrypt(number):
    number = int(number)  # تحويل الرقم إلى عدد صحيح
    encoded_bytes = []    # إنشاء قائمة لتخزين البايتات المشفرة

    while True:  # حلقة تستمر حتى يتم تشفير الرقم بالكامل
        byte = number & 0x7F  # استخراج أقل 7 بتات من الرقم
        number >>= 7  # تحريك الرقم لليمين بمقدار 7 بتات
        if number:
            byte |= 0x80  # تعيين البت الثامن إلى 1 إذا كان الرقم لا يزال يحتوي على بتات إضافية

        encoded_bytes.append(byte)
        if not number:
            break  # التوقف إذا لم يتبقى بتات إضافية في الرقم

    return bytes(encoded_bytes).hex()
    


def get_random_avatar():
    avatar_list = [
        '902000061', '902000060', '902000064', '902000065', '902000066', 
        '902000074', '902000075', '902000077', '902000078', '902000084', 
        '902000085', '902000087', '902000091', '902000094', '902000306', 
        '902000208', '902000209', '902000210', '902000211', '902047016', 
        '902000347', '902000305', '902000003', '902000016', '902000017', 
        '902000019', '902000020', '902000021', '902000023', '902000070', 
        '902000108', '902000011', '902049020', '902049018', '902049017', 
        '902049016', '902049015', '902049003', '902033016', '902033017', 
        '902033018', '902048018'
    ]
    random_avatar = random.choice(avatar_list)
    return random_avatar

class FF_CLIENT(threading.Thread):
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.get_tok()
    def connect(self, tok, host, port, packet, key, iv):
        global clients
        clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(port)
        clients.connect((host, port))
        clients.send(bytes.fromhex(tok))

        while True:
            data = clients.recv(9999)
            if data == b"":
                print("Connection closed by remote host")
                break
def get_available_room(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = parse_results(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"error {e}")
        return None

def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data["wire_type"] = result.wire_type
        if result.wire_type == "varint":
            field_data["data"] = result.data
        if result.wire_type == "string":
            field_data["data"] = result.data
        if result.wire_type == "bytes":
            field_data["data"] = result.data
        elif result.wire_type == "length_delimited":
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict
def dec_to_hex(ask):
    ask_result = hex(ask)
    final_result = str(ask_result)[2:]
    if len(final_result) == 1:
        final_result = "0" + final_result
    return final_result

def encrypt_message(plaintext):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(plaintext, AES.block_size)
    encrypted_message = cipher.encrypt(padded_message)
    return binascii.hexlify(encrypted_message).decode('utf-8')

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def extract_jwt_from_hex(hex):
    byte_data = binascii.unhexlify(hex)
    message = jwt_generator_pb2.Garena_420()
    message.ParseFromString(byte_data)
    json_output = MessageToJson(message)
    token_data = json.loads(json_output)
    return token_data
    

def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def restart_program():
    p = psutil.Process(os.getpid())
    open_files = p.open_files()
   # connections = psutil.net_connections()
    for handler in open_files:
        try:
            os.close(handler.fd)
        except Exception:
            pass
            
   # for conn in connections:
        try:
            conn.close()
        except Exception:
            pass
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)
          
class FF_CLIENT(threading.Thread):
    def __init__(self, id, password):
        super().__init__()
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.get_tok()

    def parse_my_message(self, serialized_data):
        try:
            MajorLogRes = MajorLoginRes_pb2.MajorLoginRes()
            MajorLogRes.ParseFromString(serialized_data)
            key = MajorLogRes.ak
            iv = MajorLogRes.aiv
            if isinstance(key, bytes):
                key = key.hex()
            if isinstance(iv, bytes):
                iv = iv.hex()
            self.key = key
            self.iv = iv
            print(f"Key: {self.key} | IV: {self.iv}")
            return self.key, self.iv
        except Exception as e:
            print(f"{e}")
            return None, None
            
    def nmnmmmmn(self, data):
        key, iv = self.key, self.iv
        try:
            key = key if isinstance(key, bytes) else bytes.fromhex(key)
            iv = iv if isinstance(iv, bytes) else bytes.fromhex(iv)
            data = bytes.fromhex(data)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cipher_text = cipher.encrypt(pad(data, AES.block_size))
            return cipher_text.hex()
        except Exception as e:
            print(f"Error in nmnmmmmn: {e}")
    def send_emote(self, target_id, emote_id):
        """
        Creates and prepares the packet for sending an emote to a target player.
        """
        fields = {
            1: 21,
            2: {
                1: 804266880,  
                2: 909000001,  
                5: {
                    1: int(target_id),
                    3: int(emote_id),
                }
            }
        }
        packet = create_protobuf_packet(fields).hex()
        # The packet type '0515' is used for online/squad actions
        header_lenth = len(encrypt_packet(packet, self.key, self.iv)) // 2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        else:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)    
        
    def spam_room(self, idroom, idplayer):
        fields = {
        1: 78,
        2: {
            1: int(idroom),
            2: "[C][B]L9BI7E[FF0000]BOT",
            4: 330,
            5: 6000,
            6: 201,
            10: int(get_random_avatar()),
            11: int(idplayer),
            12: 1
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def send_squad(self, idplayer):
        fields = {
            1: 33,
            2: {
                1: int(idplayer),
                2: "ME",
                3: 1,
                4: 1,
                7: 330,
                8: 19459,
                9: 100,
                12: 1,
                16: 1,
                17: {
                2: 94,
                6: 11,
                8: "1.109.5",
                9: 3,
                10: 2
                },
                18: 201,
                23: {
                2: 1,
                3: 1
                },
                24: int(get_random_avatar()),
                26: {},
                28: {}
            }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
        
    def request_join_squad(self, idplayer):
        import random
        same_value = random.choice([4096, 16384, 8192])
        fields = {
        1: 33,
        2: {
            1: int(idplayer),
            2: "ME",
            3: 1,
            4: 1,
            5: bytes([1, 7, 9, 10, 11, 18, 25, 26, 32]),
            6: "𝑳𝟗𝑩𝑰𝟕𝑬 𝑶𝑭𝑭𝑰𝑪𝑰𝑬𝑳:[C][B][FF0000] @chihab208",
            7: 330,
            8: 1000,
            10: "ME",
            11: bytes([49, 97, 99, 52, 98, 56, 48, 101, 99, 102, 48, 52, 55, 56,
            97, 52, 52, 50, 48, 51, 98, 102, 56, 102, 97, 99, 54, 49, 50, 48, 102, 53]),
            12: 1,
            13: int(idplayer),
            14: {
            1: 2203434355,
            2: 8,
            3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
            },
            16: 1,
            17: 1,
            18: 312,
            19: 46,
            23: bytes([16, 1, 24, 1]),
            24: int(get_random_avatar()),
            26: "",
            28: "",
            31: {
            1: 1,
            2: same_value
            },
            32: same_value,
            34: {
            1: int(idplayer),
            2: 8,
            3: bytes([15,6,21,8,10,11,19,12,17,4,14,20,7,2,1,5,16,3,13,18])
            }
        },
        10: "en",
        13: {
            2: 1,
            3: 1
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

    def start_autooo(self):
        fields = {
        1: 9,
        2: {
            1: 11371687918
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def invite_skwad(self, idplayer):
        fields = {
        1: 2,
        2: {
            1: int(idplayer),
            2: "ME",
            4: 1
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
        
    def request_skwad(self, idplayer):
        fields = {
        1: 33,
        2: {
            1: int(idplayer),
            2: "ME",
            3: 1,
            4: 1,
            7: 330,
            8: 19459,
            9: 100,
            12: 1,
            16: 1,
            17: {
            2: 94,
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
            18: 201,
            23: {
            2: 1,
            3: 1
            },
            24: int(get_random_avatar()),
            26: {},
            28: {}
        }
        }
        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def skwad_maker(self):
        fields = {
        1: 1,
        2: {
            2: "\u0001",
            3: 1,
            4: 1,
            5: "en",
            9: 1,
            11: 1,
            13: 1,
            14: {
            2: 5756,
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def changes(self, num):
        fields = {
        1: 17,
        2: {
            1: 11371687918,
            2: 1,
            3: int(num),
            4: 62,
            5: "\u001a",
            8: 5,
            13: 329
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)   
    def leave_s(self):
        fields = {
        1: 7,
        2: {
            1: 11371687918
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def leave_room(self, idroom):
        fields = {
        1: 6,
        2: {
            1: int(idroom)
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def stauts_infoo(self, idd):
        fields = {
        1: 7,
        2: {
            1: 11371687918
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    
    def GenResponsMsg(self, Msg, Enc_Id):
        fields = {
            1: 1,
            2: {
                1: 12947146032,
                2: Enc_Id,
                3: 2,
                4: str(Msg),
                5: int(datetime.now().timestamp()),
                7: 2,
                9: {
                    1: "BANECIPHER",
                    2: int(get_random_avatar()),
                    3: 901049014,
                    4: 330,
                    5: 710037095,
                    8: "Friend",
                    10: 1,
                    11: 1,
                    13: {
                        1: 2,
                        2: 1,
                    },
                    14: {
                        1: 11017917409,
                        2: 8,
                        3: "\u0010\u0015\b\n\u000b\u0013\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"
                    }
                },
                10: "IND",
                13: {
                    1: "https://graph.facebook.com/v9.0/253082355523299/picture?width=160&height=160",
                    2: 1,
                    3: 1
                },
                14: {
                    1: {
                        1: random.choice([1, 4]),
                        2: 1,
                        3: random.randint(1, 180),
                        4: 1,
                        5: int(datetime.now().timestamp()),
                        6: "IND"
                    }
                }
            }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "1215000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "121500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "12150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "1215000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

    def createpacketinfo(self, idddd):
        ida = Encrypt(idddd)
        packet = f"080112090A05{ida}1005"
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0F15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0F1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0F150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0F15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def accept_sq(self, hashteam, idplayer, ownerr):
        fields = {
        1: 4,
        2: {
            1: int(ownerr),
            3: int(idplayer),
            4: "\u0001\u0007\t\n\u0012\u0019\u001a ",
            8: 1,
            9: {
            2: 1393,
            4: "L9BI7E_BOT",
            6: 11,
            8: "1.109.5",
            9: 3,
            10: 2
            },
            10: hashteam,
            12: 1,
            13: "en",
            16: "OR"
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0515000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "051500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "05150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0515000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)
    def info_room(self, idrooom):
        fields = {
        1: 1,
        2: {
            1: int(idrooom),
            3: {},
            4: 1,
            6: "en"
        }
        }

        packet = create_protobuf_packet(fields)
        packet = packet.hex()
        header_lenth = len(encrypt_packet(packet, key, iv))//2
        header_lenth_final = dec_to_hex(header_lenth)
        if len(header_lenth_final) == 2:
            final_packet = "0E15000000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 3:
            final_packet = "0E1500000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 4:
            final_packet = "0E150000" + header_lenth_final + self.nmnmmmmn(packet)
        elif len(header_lenth_final) == 5:
            final_packet = "0E15000" + header_lenth_final + self.nmnmmmmn(packet)
        return bytes.fromhex(final_packet)

    def sockf1(self, tok, online_ip, online_port, packet, key, iv):
        global socket_client
        global sent_inv
        global tempid
        global start_par
        global clients
        global pleaseaccept
        global tempdata1
        global nameinv
        global idinv
        global senthi
        global statusinfo
        global tempdata
        global data22
        global leaveee
        global isroom
        global isroom2
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        online_port = int(online_port)

        socket_client.connect((online_ip,online_port))
        print(f" Con port {online_port} Host {online_ip} ")
        print(tok)
        socket_client.send(bytes.fromhex(tok))
        while True:
            data2 = socket_client.recv(9999)
            print(data2)
            if "0500" in data2.hex()[0:4]:
                accept_packet = f'08{data2.hex().split("08", 1)[1]}'
                kk = get_available_room(accept_packet)
                parsed_data = json.loads(kk)
                fark = parsed_data.get("4", {}).get("data", None)
                if fark is not None:
                    print(f"haaaaaaaaaaaaaaaaaaaaaaho {fark}")
                    if fark == 18:
                        if sent_inv:
                            accept_packet = f'08{data2.hex().split("08", 1)[1]}'
                            print(accept_packet)
                            print(tempid)
                            aa = gethashteam(accept_packet)
                            ownerid = getownteam(accept_packet)
                            print(ownerid)
                            print(aa)
                            ss = self.accept_sq(aa, tempid, int(ownerid))
                            socket_client.send(ss)
                            sleep(1)
                            startauto = self.start_autooo()
                            socket_client.send(startauto)
                            start_par = False
                            sent_inv = False
                    if fark == 6:
                        leaveee = True
                        print("kaynaaaaaaaaaaaaaaaa")
                    if fark == 50:
                        pleaseaccept = True
                print(data2.hex())

            if "0600" in data2.hex()[0:4] and len(data2.hex()) > 700:
                    accept_packet = f'08{data2.hex().split("08", 1)[1]}'
                    kk = get_available_room(accept_packet)
                    parsed_data = json.loads(kk)
                    print(parsed_data)
                    idinv = parsed_data["5"]["data"]["1"]["data"]
                    nameinv = parsed_data["5"]["data"]["3"]["data"]
                    senthi = True
            if "0f00" in data2.hex()[0:4]:
                packett = f'08{data2.hex().split("08", 1)[1]}'
                print(packett)
                kk = get_available_room(packett)
                parsed_data = json.loads(kk)
                
                asdj = parsed_data["2"]["data"]
                tempdata = get_player_status(packett)
                if asdj == 15:
                    if tempdata == "OFFLINE":
                        tempdata = f"The id is {tempdata}"
                    else:
                        idplayer = parsed_data["5"]["data"]["1"]["data"]["1"]["data"]
                        idplayer1 = fix_num(idplayer)
                        if tempdata == "IN ROOM":
                            idrooom = get_idroom_by_idplayer(packett)
                            idrooom1 = fix_num(idrooom)
                            
                            tempdata = f"id : {idplayer1}\nstatus : {tempdata}\nid room : {idrooom1}"
                            data22 = packett
                            print(data22)
                            
                        if "INSQUAD" in tempdata:
                            idleader = get_leader(packett)
                            idleader1 = fix_num(idleader)
                            tempdata = f"id : {idplayer1}\nstatus : {tempdata}\nleader id : {idleader1}"
                        else:
                            tempdata = f"id : {idplayer1}\nstatus : {tempdata}"
                    statusinfo = True 

                    print(data2.hex())
                    print(tempdata)
                
                    

                else:
                    pass
            if "0e00" in data2.hex()[0:4]:
                packett = f'08{data2.hex().split("08", 1)[1]}'
                print(packett)
                kk = get_available_room(packett)
                parsed_data = json.loads(kk)
                idplayer1 = fix_num(idplayer)
                asdj = parsed_data["2"]["data"]
                tempdata1 = get_player_status(packett)
                if asdj == 14:
                    nameroom = parsed_data["5"]["data"]["1"]["data"]["2"]["data"]
                    
                    maxplayer = parsed_data["5"]["data"]["1"]["data"]["7"]["data"]
                    maxplayer1 = fix_num(maxplayer)
                    nowplayer = parsed_data["5"]["data"]["1"]["data"]["6"]["data"]
                    nowplayer1 = fix_num(nowplayer)
                    tempdata1 = f"{tempdata}\nRoom name : {nameroom}\nMax player : {maxplayer1}\nLive player : {nowplayer1}"
                    print(tempdata1)
                    

                    
                
                    
            if data2 == b"":
                
                print("Connection closed by remote host")
                restart_program()
                break
    
    
    def connect(self, tok, packet, key, iv, whisper_ip, whisper_port, online_ip, online_port):
        global clients
        global socket_client
        global sent_inv
        global tempid
        global leaveee
        global start_par
        global nameinv
        global idinv
        global senthi
        global statusinfo
        global tempdata
        global pleaseaccept
        global tempdata1
        global data22
        clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clients.connect((whisper_ip, whisper_port))
        clients.send(bytes.fromhex(tok))
        thread = threading.Thread(
            target=self.sockf1, args=(tok, online_ip, online_port, "anything", key, iv)
        )
        threads.append(thread)
        thread.start()

        while True:
            data = clients.recv(9999)

            if data == b"":
                print("Connection closed by remote host")
                break
                print(f"Received data: {data}")

            
            if senthi == True:
                
                clients.send(
                        self.GenResponsMsg(
                            f"""[C][B][1E90FF]╔══════════════════════════╗
[FFFFFF]مرحبًا! شكرًا لإضافتي.
[FFFFFF]لمعرفة الأوامر المتاحة،
[FFFFFF]أرسل أي رسالة أو إيموجي.
[1E90FF]╠══════════════════════════╣
[FFFFFF]هل أنت مهتم بشراء البوت
[FFFFFF]تواصل مع المطور:
[FFD700]تيليجرام: @chihab208
[1E90FF]╚══════════════════════════╝""", idinv
                        )
                )
                senthi = False
            
            
            
            if "1200" in data.hex()[0:4]:
               
                json_result = get_available_room(data.hex()[10:])
                print(data.hex())
                parsed_data = json.loads(json_result)
                try:
                        uid = parsed_data["5"]["data"]["1"]["data"]
                except KeyError:
                        print("Warning: '1' key is missing in parsed_data, skipping...")
                        uid = None  # تعيين قيمة افتراضية
                if "8" in parsed_data["5"]["data"] and "data" in parsed_data["5"]["data"]["8"]:
                    uexmojiii = parsed_data["5"]["data"]["8"]["data"]
                    if uexmojiii == "DefaultMessageWithKey":
                        pass
                    else:
                        clients.send(
                            self.GenResponsMsg(
                            f"""[33FFF3][c][b]-----------------------------------

[11EAFDَ][bَ][c]للحصول على قائمة الأوامر الكاملة، يرجى كتابة:

[99FF80َ][c][b]ِ @ُhِeِlِp

[33FFF3][c][b]-----------------------------------

[FF0000] my telegrame :@chihab208

[b][c][00FFFF]╏Dev by: 𝑳𝟗𝑩𝑰𝟕𝑬 𝑶𝑭𝑭𝑰𝑪𝑰𝑬𝑳

[FFFFFF]تم صنع هذا البوت رسميا لنكح اللاعبين
[33FFF3][c][b]-----------------------------------""",uid
                            )
                        )
                else:
                    pass  


                    
                


            if "1200" in data.hex()[0:4] and b"@admin" in data:
                i = re.split("@admin", str(data))[1]
                if "***" in i:
                    i = i.replace("***", "106")
                sid = str(i).split("(\\x")[0]
                json_result = get_available_room(data.hex()[10:])
                
                parsed_data = json.loads(json_result)
                uid = parsed_data["5"]["data"]["1"]["data"]
                clients.send(
                    self.GenResponsMsg(
                        f"""[C][B][FF00FF]
 telegram:@chihab208
 
[b][i][A5E2CFٍ] Dev: Chihab""", uid
                    )
                )
           
                                      

            if "1200" in data.hex()[0:4] and b"@3" in data:
                # يแยก i من الأمر @3
                i = re.split("@3", str(data))[1]
                if "***" in i:
                    i = i.replace("***", "106")
                sid = str(i).split("(\\x")[0]
                
                # استخراج بيانات اللاعب المرسل
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)
                uid = parsed_data["5"]["data"]["1"]["data"]

                # 1. إنشاء فريق جديد
                packetmaker = self.skwad_maker()
                socket_client.send(packetmaker)
                sleep(0.5)  # انتظر قليلاً لضمان إنشاء الفريق

                # 2. تغيير وضع الفريق إلى 3 لاعبين (2 = 3-1)
                packetfinal = self.changes(2)
                socket_client.send(packetfinal)
                sleep(0.5)

                # 3. التحقق مما إذا كان هناك ID لدعوته
                room_data = None
                if b'(' in data:
                    split_data = data.split(b'@3')
                    if len(split_data) > 1:
                        room_data = split_data[1].split(
                            b'(')[0].decode().strip().split()
                        if room_data:
                            iddd = room_data[0]
                            # إرسال دعوة للاعب المحدد
                            invitess = self.invite_skwad(iddd)
                            socket_client.send(invitess)
                        else:
                            # إذا لم يتم تحديد ID، يتم دعوة الشخص الذي أرسل الأمر
                            iddd = uid
                            invitess = self.invite_skwad(iddd)
                            socket_client.send(invitess)

                # 4. إرسال رسالة تأكيد للمستخدم
                if uid:
                    clients.send(
                        self.GenResponsMsg(
                            f"[C][B][1E90FF]-----------------------------\n\n\n\nجاري  تحويل الفريق الي  ثلاثي\n\n\n\n-----------------------------",
                            uid
                        )
                    )

                # 5. مغادرة الفريق وتغيير الوضع إلى فردي (Solo) بعد فترة
                sleep(5)  # انتظر 5 ثوانٍ
                leavee = self.leave_s()
                socket_client.send(leavee)
                sleep(1)
                change_to_solo = self.changes(1)
                socket_client.send(change_to_solo)
                    
            if "1200" in data.hex()[0:4] and b"@5" in data:
                i = re.split("@5", str(data))[1]
                if "***" in i:
                    i = i.replace("***", "106")
                sid = str(i).split("(\\x")[0]
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)

                # إنشاء الفريق
                packetmaker = self.skwad_maker()
                socket_client.send(packetmaker)

                sleep(1)

                # تعيين نوع الفريق
                packetfinal = self.changes(4)
                socket_client.send(packetfinal)

                room_data = None
                if b'(' in data:
                    split_data = data.split(b'@5')
                    if len(split_data) > 1:
                        room_data = split_data[1].split(
                            b'(')[0].decode().strip().split()
                        if room_data:
                            iddd = room_data[0]
                        else:
                            uid = parsed_data["5"]["data"]["1"]["data"]
                            iddd = parsed_data["5"]["data"]["1"]["data"]

                # إرسال الدعوة
                invitess = self.invite_skwad(iddd)
                socket_client.send(invitess)

                if uid:
                    clients.send(
                        self.GenResponsMsg(
                            f"[C][B][1E90FF]-----------------------------\n\n\n\nجاري  تحويل الفريق الي  خماسي\n\n\n\n-----------------------------",
                            uid))

                # التأكد من المغادرة بعد 5 ثوانٍ إذا لم تتم المغادرة تلقائيًا
                sleep(5)
                print("Checking if still in squad...")

                leavee = self.leave_s()
                socket_client.send(leavee)

                # تأخير أطول للتأكد من تنفيذ المغادرة قبل تغيير الوضع
                sleep(2)

                # إرسال أمر تغيير وضع اللعبة إلى Solo
                change_to_solo = self.changes(1)  # تأكد أن `1` هو القيمة الصحيحة لـ Solo
                socket_client.send(change_to_solo)

                # تأخير بسيط قبل إرسال التأكيد للمستخدم

                 

                
                    
            if "1200" in data.hex()[0:4] and b"@6" in data:
                i = re.split("@6", str(data))[1]
                if "***" in i:
                    i = i.replace("***", "106")
                sid = str(i).split("(\\x")[0]
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)
                packetmaker = self.skwad_maker()
                socket_client.send(packetmaker)
                sleep(0.5)
                packetfinal = self.changes(5)
                room_data = None
                if b'(' in data:
                    split_data = data.split(b'@6')
                    if len(split_data) > 1:
                        room_data = split_data[1].split(
                            b'(')[0].decode().strip().split()
                        if room_data:
                            iddd = room_data[0]
                        else:
                            uid = parsed_data["5"]["data"]["1"]["data"]
                            iddd = parsed_data["5"]["data"]["1"]["data"]
                socket_client.send(packetfinal)
                invitess = self.invite_skwad(iddd)
                socket_client.send(invitess)
                if uid:
                    clients.send(
                        self.GenResponsMsg(
                  f"[C][B][1E90FF]-----------------------------\n\n\n\nجاري  تحويل الفريق الي  سداسي\n\n\n\n-----------------------------",
                            uid))

                sleep(4)  # انتظار 2 ثواني
                leavee = self.leave_s()
                socket_client.send(leavee)
                sleep(0.5)
                change_to_solo = self.changes(1)  # تغيير إلى Solo
                socket_client.send(change_to_solo)

            if "1200" in data.hex()[0:4] and b"@status" in data:
                try:
                    print("Received @st command")
                    i = re.split("@status", str(data))[1]
                    if "***" in i:
                        i = i.replace("***", "106")
                    sid = str(i).split("(\\x")[0]
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    split_data = re.split(rb'@status', data)
                    room_data = split_data[1].split(b'(')[0].decode().strip().split()
                    if room_data:
                        player_id = room_data[0]
                        uid = parsed_data["5"]["data"]["1"]["data"]
                        packetmaker = self.createpacketinfo(player_id)
                        socket_client.send(packetmaker)
                        statusinfo1 = True
                        while statusinfo1:
                            if statusinfo == True:
                                if "IN ROOM" in tempdata:
                                    inforoooom = self.info_room(data22)
                                    socket_client.send(inforoooom)
                                    sleep(0.5)
                                    clients.send(self.GenResponsMsg(f"{tempdata1}", uid))  
                                    tempdata = None
                                    tempdata1 = None
                                    statusinfo = False
                                    statusinfo1 = False
                                else:
                                    clients.send(self.GenResponsMsg(f"{tempdata}", uid))  
                                    tempdata = None
                                    tempdata1 = None
                                    statusinfo = False
                                    statusinfo1 = False
                    else:
                        clients.send(self.GenResponsMsg("[C][B][FF0000] الرجاء إدخال معرف اللاعب!", uid))  
                except Exception as e:
                    print(f"Error in @rs command: {e}")
                    clients.send(self.GenResponsMsg("[C][B][FF0000]ERROR!", uid))
                                                                          
            if "1200" in data.hex()[0:4] and b"@inv" in data:
                i = re.split("@inv", str(data))[1]
                if "***" in i:
                    i = i.replace("***", "106")
                sid = str(i).split("(\\x")[0]
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)
                split_data = re.split(rb'@inv', data)
                room_data = split_data[1].split(b'(')[0].decode().strip().split()
                if room_data:
                    print(room_data)
                    iddd = room_data[0]
                    numsc1 = "5"

                    if numsc1 is None:
                        clients.send(
                            self.GenResponsMsg(
                                f"[C][B] [FF00FF]Please write id and count of the group\n[ffffff]Example : \n@ inv 123[c]456[c]78 4\n@ inv 123[c]456[c]78 5", uid
                            )
                        )
                    else:
                        numsc = int(numsc1) - 1
                        uid = parsed_data["5"]["data"]["1"]["data"]
                        if int(numsc1) < 3 or int(numsc1) > 6:
                            clients.send(
                                self.GenResponsMsg(
                                    f"[C][B][FF0000] Usage : @inv <uid> <Squad Type>\n[ffffff]Example : \n@ inv 12345678 4\n@ inv 12345678 5", uid
                                )
                            )
                        else:
                            packetmaker = self.skwad_maker()
                            socket_client.send(packetmaker)
                            sleep(1)
                            packetfinal = self.changes(int(numsc))
                            socket_client.send(packetfinal)
                            
                            invitess = self.invite_skwad(iddd)
                            socket_client.send(invitess)
                            iddd1 = parsed_data["5"]["data"]["1"]["data"]
                            invitessa = self.invite_skwad(iddd1)
                            socket_client.send(invitessa)
                            clients.send(
                        self.GenResponsMsg(
                            f"[C][B][00ff00]جاري[0000FFَ] عمل[0000FFَ] فريق[00FF00َ]وارسل لك[FF8000َ]! ", uid
                        )
                    )

                # التأكد من المغادرة بعد 5 ثوانٍ إذا لم تتم المغادرة تلقائيًا
                sleep(5)
                print("[FF8000َ]Checking [6E00FFَ]if [00FF00َ]still in [FFFF00ِ]squad...")

                leavee = self.leave_s()
                socket_client.send(leavee)

                 # تأخير أطول للتأكد من تنفيذ المغادرة قبل تغيير الوضع
                sleep(5)

                 # إرسال أمر تغيير وضع اللعبة إلى Solo
                change_to_solo = self.changes(1)  # تأكد أن `1` هو القيمة الصحيحة لـ Solo
                socket_client.send(change_to_solo)

                 # تأخير بسيط قبل إرسال التأكيد للمستخدم
                sleep(0.1)

                clients.send(
                     self.GenResponsMsg(
                         f"[C][B] [FF00FF]البوت [6E00FFَ] اصبح [00FF00َ]سلو  [FF8000َ]الان.", uid
                     )
                 )
                          
                                                                          
            if "1200" in data.hex()[0:4] and b"@room" in data:
                i = re.split("@room", str(data))[1] 
                sid = str(i).split("(\\x")[0]
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)
                uid = parsed_data["5"]["data"]["1"]["data"]
                split_data = re.split(rb'@room', data)
                room_data = split_data[1].split(b'(')[0].decode().strip().split()
                if room_data:
                    
                    player_id = room_data[0]
                    if player_id.isdigit():
                        if "***" in player_id:
                            player_id = rrrrrrrrrrrrrr(player_id)
                        packetmaker = self.createpacketinfo(player_id)
                        socket_client.send(packetmaker)
                        sleep(0.5)
                        if "IN ROOM" in tempdata:
                            room_id = get_idroom_by_idplayer(data22)
                            packetspam = self.spam_room(room_id, player_id)
                            print(packetspam.hex())
                            clients.send(
                                self.GenResponsMsg(
                                    f"[C][B][00ff00]جاري العمل علي طلب {fix_num(player_id)} ! ", uid
                                )
                            )
                            
                            
                            for _ in range(99):

                                print(" sending spam to "+player_id)
                                threading.Thread(target=socket_client.send, args=(packetspam,)).start()
                            #socket_client.send(packetspam)
                            
                            
                            
                            clients.send(
                                self.GenResponsMsg(
                                    f"[C][B] [00FF00]نجح الطلب", uid
                                )
                            )
                        else:
                            clients.send(
                                self.GenResponsMsg(
                                    f"[C][B] [FF00FF]The player is not in room", uid
                                )
                            )      
                    else:
                        clients.send(
                            self.GenResponsMsg(
                                f"[C][B] [FF00FF]Please write the id of player not!", uid
                            )
                        )   

                else:
                    clients.send(
                        self.GenResponsMsg(
                            f"[C][B] [FF00FF]Please write the id of player !", uid
                        )
                    )   
            

            
            

            if "1200" in data.hex()[0:4] and b"WELCOME TO L9BI7EDevX BOT" in data:
                pass
            else:
             
                    if "1200" in data.hex()[0:4] and b"@biccco" in data:
                           try:
                                print("✅ @biccco command detected.")  
                                command_split = re.split("@biccco", str(data))

                                if len(command_split) <= 1 or not command_split[1].strip():
                                       print("❌ No ID provided, sending error message.")
                                       json_result = get_available_room(data.hex()[10:])
                                       parsed_data = json.loads(json_result)
                                       sender_id = parsed_data["5"]["data"]["1"]["data"]
                                       clients.send(
                                           self.GenResponsMsg(
                                               "[C][B][FF0000] Please enter a valid player ID!",
                                               sender_id
                                           )
                                       )
                                else:
                                       print("✅ Command has parameters.")  
                                       json_result = get_available_room(data.hex()[10:])
                                       parsed_data = json.loads(json_result)

                                       sender_id = parsed_data["5"]["data"]["1"]["data"]
                                       sender_name = parsed_data['5']['data']['9']['data']['1']['data']
                                       print(f"✅ Sender ID: {sender_id}, Sender Name: {sender_name}")  

                                       uids = re.findall(r"\b\d{5,15}\b", command_split[1])
                                       uid = uids[0] if uids else ""

                                       if not uid:
                                              print("❌ No valid UID found, sending error message.")
                                              clients.send(
                                                  self.GenResponsMsg(
                                                      "[C][B][FF0000] معرف اللاعب غير صالح!",
                                                      sender_id
                                                  )
                                              )
                                       else:
                                              print(f"✅ Extracted UID: {uid}")  

                                              try:
                                                  info_response = newinfo(uid)
                                                  print(f"✅ API Response Received: {info_response}")  
                                              except Exception as e:
                                                  print(f"❌ API Error: {e}")
                                                  clients.send(
                                                      self.GenResponsMsg(
                                                          "[C][B][FF0000] Server Error, Try Again!",
                                                          sender_id
                                                      )
                                                  )
                                                  continue
                                                  
                                              if 'info' not in info_response or info_response['status'] != "ok":
                                                     print("❌ Invalid ID or API Error, sending wrong ID message.")
                                                     clients.send(
                                                         self.GenResponsMsg(
                                                             "[C][B][FF0000] Wrong ID .. Please Check Again",
                                                             sender_id
                                                         )
                                                     )
                                              else:
                                                     print("✅ Valid API Response, Extracting Player Info.")  
                                                     infoo = info_response['info']
                                                     basic_info = infoo['basic_info']
                                                     
                                                     bio = basic_info.get('bio', "No bio available").replace("|", " ")
                                                     
                                                     if bio == "No bio available" or not bio.strip():
                                                            message_info = (
                                                                f"[C][B][00FF00]«—————— 🖊️ البايو ——————»\n"
                                                                f"[B][FFFFFF]لا يوجد بايو\n"
                                                                f"[C][B][00FF00]«————————— النهاية —————————»"
                                                            )
                                                     else:
                                                            message_info = (
                                                                f"[C][B][00FF00]«—————— 🖊️ البايو ——————»\n"
                                                                f"[B][FFFFFF]{bio}\n"
                                                                f"[C][B][00FF00]«————————— النهاية —————————»"
                                                            )

                                                     print(f"📤 Sending message to game: {message_info}")  

                                                     try:
                                                            clients.send(self.GenResponsMsg(message_info, sender_id))
                                                            print("✅ Message Sent Successfully!")  
                                                     except Exception as e:
                                                            print(f"❌ Error sending message: {e}")
                                                            clients.send(
                                                                self.GenResponsMsg(
                                                                    "[C][B][FF0000] Failed to send message!",
                                                                    sender_id
                                                                )
                                                            )
                           except Exception as e:
                                print(f"❌ Unexpected Error: {e}")
                                clients.send(
                                    self.GenResponsMsg(
                                        "[C][B][FF0000] An unexpected error occurred!",
                                        sender_id
                                    )
                                )
                            
                            
                            
                        
                    if "1200" in data.hex()[0:4] and b"@check" in data:
                           try:
                                print("Received @check command")
                                command_split = re.split("@check", str(data))
                                json_result = get_available_room(data.hex()[10:])
                                parsed_data = json.loads(json_result)
                                uid = parsed_data["5"]["data"]["1"]["data"]
                                
                                clients.send(
                                    self.GenResponsMsg(
                                        f"{generate_random_color()}جاري فحص حالة الباند...", uid
                                    )
                                )
                                
                                if len(command_split) > 1:
                                       command_text = command_split[1].split('(')[0].strip()
                                       uids = re.findall(r"\b\d{5,15}\b", command_text)
                                       player_id = uids[0] if uids else ""
                                       
                                       if not player_id:
                                              clients.send(
                                                  self.GenResponsMsg(
                                                      "[C][B][FF0000]الرجاء إدخال معرف لاعب صحيح!", uid
                                                  )
                                              )
                                              continue

                                       print(f"🔍 Checking ban status for: {player_id}")

                                       banned_status = check_banned_status(player_id)
                                       print(f"📊 Ban check result: {banned_status}")
                                       
                                       if "error" in banned_status:
                                              clients.send(
                                                  self.GenResponsMsg(
                                                      f"[C][B][FF0000]خطأ: {banned_status['error']}", uid
                                                  )
                                              )
                                              continue

                                       player_id_formatted = fix_num(player_id)
                                       status = banned_status.get('status', 'Unknown')
                                       player_name = banned_status.get('player_name', 'Unknown')
                                       region = banned_status.get('region', 'Unknown')
                                       ban_period = banned_status.get('ban_period', 0)
                                       
                                       if "مبند" in status and "❌" in status:
                                              status_color = "[FF0000]"
                                              status_text = "❌ Banned"
                                       else:
                                              status_color = "[00FF00]"
                                              status_text = "✅ Not Banned"

                                       response_message = (
                                           f"{generate_random_color()}——————————\n"
                                           f"👤 Name: {player_name}\n"
                                           f"🆔 ID: {player_id_formatted}\n"
                                           f"📊 Status: {status_color}{status_text}\n"
                                           f"🌍 Region: {region}\n"
                                           f"⏰ Ban Period: {ban_period} days\n"
                                           f"——————————"
                                       )
                                       
                                       print("📤 Sending ban check result to game")
                                       clients.send(self.GenResponsMsg(response_message, uid))
                           except Exception as e:
                                print(f"❌ Error in @check command: {e}")
                                import traceback
                                traceback.print_exc()
                                try:
                                     clients.send(
                                         self.GenResponsMsg(
                                             "[C][B][FF0000]حدث خطأ أثناء فحص الباند!", uid
                                         )
                                     )
                                except:
                                     pass

                    if "1200" in data.hex()[0:4] and b"@help" in data:
                        
                        lines = "_"*20
                        
                        json_result = get_available_room(data.hex()[10:])
                        parsed_data = json.loads(json_result)
                        user_name = parsed_data['5']['data']['9']['data']['1']['data']
                        uid = parsed_data["5"]["data"]["1"]["data"]
                        if "***" in str(uid):
                                uid = rrrrrrrrrrrrrr(uid)
                        
                        print(f"\nUser With ID : {uid}\nName : {user_name}\nStarted Help\n")
 
                        clients.send(
                                    self.GenResponsMsg(
                                        f"""[C][B][33FFF3]\n\n\nمرحبًا {user_name}\n\n\n""",uid
                            )
                        )
                        
                        time.sleep(0.5)
                        clients.send(
                                    self.GenResponsMsg(
                                      f"""
[b][c][FF00FF]◈━─  L9BI7E BOT  ─━◈
[FFFFFF]━━━━━━━━━━━━━━━

[00FFFF]💠 [FFFFFF]TEAM [00FFFF]𝟯 [FFFFFF]➔ [00FFFF]@3

[FF8C00]💠 [FFFFFF]TEAM [FF8C00]𝟱 [FFFFFF]➔ [00FFFF]@5

[FF0000]💠 [FFFFFF]TEAM [FF0000]𝟲 [FFFFFF]➔ [00FFFF]@6

[FFFFFF]━━━━━━━━━━━━━━━
[00FFFF]⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ʟ9ʙɪ7ᴇ ⚡
""", uid

                            )
                        )                       
                                                            
                        time.sleep(0.5)
                        clients.send(
                                    self.GenResponsMsg(
                                        f"""[C][B]
[b][c][FF00FF]⚡ L9BI7E SERVICES ⚡
[FFFF00]━━━━━━━━━━━━━━

[FFFFFF]📂 [00FFFF]Open Team 5 [FFFFFF]➜ [00FFFF]@inv [id]

[FFFFFF]💠 [FF8C00]Spam Team [FFFFFF]➜ [00FFFF]@sp [id]

[FFFFFF]🚪 [FF0000]Spam Room [FFFFFF]➜ [00FFFF]@room [id]

[FFFF00]━━━━━━━━━━━━━━
[00FFFF]➲ [FFFFFF]Fast & Pro Control
""", uid

                            )
                        )                               
                        
                        time.sleep(0.5)
                        clients.send(
                                    self.GenResponsMsg(
                                                f"""[C][B]
                                              
[b][c][00FFFF]◈━━━━━━━━━━━━━━━◈

[FF00FF]🛰️ [FFFFFF]Squad Info [FF00FF]➔ [00FFFF]@status <id>

[FF00FF]⚡ [FFFFFF]Pull Player [FF00FF]➔ [00FFFF]@send <id>

[FF00FF]🛡️ [FFFFFF]Ban Check  [FF00FF]➔ [00FFFF]@check <id>

[00FFFF]◈━━━━━━━━━━━━━━━◈
[FFFF00]➲ [FFFFFF]Control Your Game Now!
""", uid

                            )
                       ) 
                       
                       
                        time.sleep(0.5)
                        clients.send(
                                    self.GenResponsMsg(
                                        f"""     [b][c][00FF00]◈━━━━━━━━━━━━━◈
[FFA500]🕺 [FFFFFF]Emote Squad [FFA500]➔ [00FFFF]@emote [UID] [T.C] [ID]

[FFA500]📜 [FFFFFF]Get Player Bio [FFA500]➔ [00FFFF]@bio [ID]

[FFA500]⚔️ [FFFFFF]Force Start [FFA500]➔ [00FFFF]@attack [T.C]

[FFA500]👻 [FFFFFF]Ghost Mode [FFA500]➔ [00FFFF]@ghost [T.C] [Name]

[00FF00]◈━━━━━━━━━━━━━◈
[00FFFF]➲ [FFFFFF]L9BI7E [00FF00]V1.2 [FFFFFF]ACTIVE
""",uid

                            )
                       ) 
                       
                                             
                        time.sleep(0.5)
                        clients.send(
                                    self.GenResponsMsg(
                                        f"""   
[b][c][FF0000]◈━━━━━━━━━━━━━━◈

[FFFFFF]🚪 [FF0000]Exit Squad [FFFFFF]➜ [00FFFF]@solo

[FFFFFF]💤 [FF0000]Rest Mode (10s) [FFFFFF]➜ [00FFFF]@rest

[FF0000]◈━━━━━━━━━━━━━━◈
[FFFFFF]➲ [00FFFF]L9BI7E [FFFFFF]Control System
""",uid
                            )
                       )        
                                                            
                    
            if "1200" in data.hex()[0:4] and b"@ghost" in data:
                handle_code_command(data, clients, socket_client, key, iv, get_available_room, self.GenResponsMsg)
                
                
            if "1200" in data.hex()[0:4] and b"@sp" in data:  
                try:  
                    # Get the UID of the user who sent the command to send a reply  
                    json_result = get_available_room(data.hex()[10:])  
                    parsed_data = json.loads(json_result)  
                    uid = parsed_data["5"]["data"]["1"]["data"]  

                    # Improved Parsing: Use a regular expression to find the ID more reliably  
                    match = re.search(r'@sp\s*(\d+)', str(data))  
                      
                    if match:  
                        player_id_str = match.group(1)  

                        # Send an initial confirmation message  
                        clients.send(  
                            self.GenResponsMsg(  
                                f"[C][B][1E90FF]جاري إرسال 300 طلب انضمام للاعب : {fix_num(player_id_str)}...", uid  
                            )  
                        )  

                        # --- START OF THE FIX ---  
                        # 1. Ensure the bot is not in a squad before starting the spam.  
                        # This is the critical step that was missing.  
                        logging.info("Resetting bot state to solo before @sp spam.")  
                        socket_client.send(self.leave_s())  
                        time.sleep(0.5)  # Allow a moment for the leave command to process  
                        socket_client.send(self.changes(1)) # Change mode to solo  
                        time.sleep(0.5)  # Allow a moment for the mode change  
                        # --- END OF THE FIX ---  

                        # Create the request packet for the target player  
                        invskwad_packet = self.request_join_squad(player_id_str)  
                        spam_count = 300  # You can adjust this value  

                        # Loop to send the packet multiple times  
                        for _ in range(spam_count):  
                            socket_client.send(invskwad_packet)  
                            sleep(0.1)  # A small delay to prevent server issues  

                        # Send a final success message  
                        clients.send(  
                            self.GenResponsMsg(  
                                f"[C][B][00FF00] تم إرسال 300 طلب انضمام بنجاح!", uid  
                            )  
                        )  

                        # Post-spam cleanup is still good practice.  
                        sleep(1)  
                        socket_client.send(self.leave_s())  
                      
                    else:  
                        # Handle cases where the player ID is missing or invalid  
                        clients.send(  
                            self.GenResponsMsg(  
                                "[C][B][FF0000]❌ صيغة الأمر غير صالحة. الرجاء استخدام: @sp <معرف_اللاعب>", uid  
                            )  
                        )  

                except Exception as e:  
                    logging.error(f"Error in @sp command: {e}. Restarting.")  
                    try:  
                        # Attempt to notify the user about the error before restarting  
                        json_result = get_available_room(data.hex()[10:])  
                        parsed_data = json.loads(json_result)  
                        uid = parsed_data["5"]["data"]["1"]["data"]  
                        clients.send(self.GenResponsMsg("[C][B][FF0000]❌ حدث خطأ. جاري إعادة تشغيل البوت...", uid))  
                    except:  
                        pass   
                    restart_program()                
                
                
            if "1200" in data.hex()[0:4] and b"@solo" in data:
                json_result = get_available_room(data.hex()[10:])
                parsed_data = json.loads(json_result)
                uid = parsed_data["5"]["data"]["1"]["data"]

                # إرسال أمر مغادرة الفريق
                leavee = self.leave_s()
                socket_client.send(leavee)

                sleep(1)  # انتظار للتأكد من تنفيذ الخروج

                # تغيير الوضع إلى Solo
                change_to_solo = self.changes(1)
                socket_client.send(change_to_solo)

                

                clients.send(
                    self.GenResponsMsg(
                        f"[C][B][00FF00] تم الخروج من المجموعة.", uid
                    )
                )
                        
                        
            if "1200" in data.hex()[0:4] and b"@emote" in data:
                try:
                    # --- START: Load Emotes from JSON file ---
                    emote_map = {}
                    try:
                        with open('emotes.json', 'r') as f:
                            emotes_data = json.load(f)
                            for emote_entry in emotes_data:
                                emote_map[emote_entry['Number']] = emote_entry['Id']
                    
                    except FileNotFoundError:
                        logging.error("CRITICAL: emotes.json file not found! The @emote command is disabled.")
                        json_result = get_available_room(data.hex()[10:])
                        uid_sender = json.loads(json_result)["5"]["data"]["1"]["data"]
                        clients.send(self.GenResponsMsg(
                            "[C][B][FF0000]❌ خطأ: ملف emotes.json مفقود. الرجاء التواصل مع المسؤول.", uid_sender
                        ))
                        continue
                    
                    except (json.JSONDecodeError, KeyError):
                        logging.error("CRITICAL: emotes.json is formatted incorrectly! The @emote command is disabled.")
                        json_result = get_available_room(data.hex()[10:])
                        uid_sender = json.loads(json_result)["5"]["data"]["1"]["data"]
                        clients.send(self.GenResponsMsg(
                            "[C][B][FF0000]❌ خطأ: ملف الإيموهات تالف. الرجاء التواصل مع المسؤول.", uid_sender
                        ))
                        continue
                    # --- END: Load Emotes from JSON file ---

                    # Get the sender's UID to send replies
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid_sender = parsed_data["5"]["data"]["1"]["data"]

                    # Parse the command parts
                    command_parts = data.split(b'@emote')[1].split(b'(')[0].decode().strip().split()
                    
                    if len(command_parts) < 2:
                        clients.send(self.GenResponsMsg(
                            f"[C][B][FF0000]❌ طريقة الاستخدام: @emote [uid1] [uid2] [uid3] [team_cod] [رقم الرقصة]\n"
                            f"[FFFF00]ملاحظة: يوجد رقصات من 1 إلى 409", uid_sender
                        ))
                        continue

                    emote_choice = command_parts[-1]
                    team_code = command_parts[-2]
                    target_ids = command_parts[:-2]
                    
                    # Check if emote number is valid
                    if emote_choice not in emote_map:
                        max_emote_number = len(emote_map)
                        clients.send(self.GenResponsMsg(
                            f"[C][B][FF0000]❌ رقم الرقصة غير صحيح!\n"
                            f"[FFFF00]الرجاء استخدام رقم بين 1 و {max_emote_number}\n"
                            f"[00FFFF]ملاحظة: يوجد رقصات من 1 إلى 409", uid_sender
                        ))
                        continue
                    
                    emote_id_to_send = emote_map[emote_choice]

                    clients.send(self.GenResponsMsg(
                        f"[C][B][00FF00]🎭 جاري الانضمام للفريق {team_code} وإرسال الرقصة #{emote_choice} إلى {len(target_ids)} لاعب...", uid_sender
                    ))
                    
                    # Step 1: Join the team
                    join_teamcode(socket_client, team_code, self.key, self.iv)
                    time.sleep(2)  # Wait to ensure joining
                    
                    clients.send(self.GenResponsMsg(
                        f"[C][B][00FF00]✅ تم الانضمام للفريق بنجاح! جاري إرسال الرقصات...", uid_sender
                    ))
                    
                    # Step 2: Send emote to each target with 0.5 second delay
                    for i, target_id in enumerate(target_ids, 1):
                        if target_id.isdigit() and emote_id_to_send.isdigit():
                            emote_packet = self.send_emote(target_id, emote_id_to_send)
                            socket_client.send(emote_packet)
                            clients.send(self.GenResponsMsg(
                                f"[C][B][FFFF00]🔄 إرسال الرقصة #{emote_choice} إلى اللاعب {i} من {len(target_ids)}...", uid_sender
                            ))
                            time.sleep(0.5)
                    
                    clients.send(self.GenResponsMsg(
                        f"[C][B][00FF00]✅ تم إرسال جميع الرقصات بنجاح! جاري الانتظار...", uid_sender
                    ))
                    
                    # Step 3: Wait 3 seconds
                    time.sleep(3)
                    
                    # Step 4: Leave the team
                    leave_packet = self.leave_s()
                    socket_client.send(leave_packet)
                    
                    clients.send(self.GenResponsMsg(
                        f"[C][B][00FF00]🎉 تم إنهاء أمر الرقص بنجاح! تم الخروج من الفريق.", uid_sender
                    ))

                except Exception as e:
                    logging.error(f"Error processing @emote command: {e}")
                    try:
                        json_result = get_available_room(data.hex()[10:])
                        uid = json.loads(json_result)["5"]["data"]["1"]["data"]
                        clients.send(self.GenResponsMsg("[C][B][FF0000]❌ حدث خطأ أثناء تنفيذ أمر الرقص.", uid))
                    except:
                        pass                
                
                
            if "1200" in data.hex()[0:4] and b"@rest" in data:
                try:
                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]

                    # إرسال رسالة تأكيد بدء الراحة
                    clients.send(
                        self.GenResponsMsg(f"[C][B][00FFFF]🛌 وضع الراحة مفعل...\n[C][B][FFFF00]البوت سيتوقف لمدة 10 ثوان", uid)
                    )

                    # فترة راحة 10 ثوان
                    sleep(10)

                    # إرسال رسالة انتهاء الراحة
                    clients.send(
                        self.GenResponsMsg(f"[C][B][00FF00]✅ انتهت فترة الراحة!\n[C][B][FFA500]البوت جاهز للعمل مرة أخرى", uid)
                    )

                except Exception as e:
                    print(f"Error in @rest command: {e}")
                    try:
                        clients.send(self.GenResponsMsg("[C][B][FF0000]❌ خطأ في أمر الراحة", uid))
                    except:
                        pass

            if "1200" in data.hex()[0:4] and b"@come" in data:
                try:
                    # تقسيم البيانات القادمة بعد الأمر
                    split_data = re.split(rb'@come', data)
                    command_parts = split_data[1].split(b'(')[0].decode().strip().split()

                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data["5"]["data"]["1"]["data"]

                    # التحقق من وجود كود التيم
                    if not command_parts:
                        clients.send(self.GenResponsMsg("[C][B][FF0000]🔴 الرجاء إدخال كود التيم!\n[C][B][FFFF00]مثال: @come ABCD1234", uid))
                        continue

                    team_code = command_parts[0]
                    
                    # إعلام المستخدم ببدء عملية الانضمام
                    clients.send(
                        self.GenResponsMsg(f"[C][B][00FFFF]🤖 البوت يحاول الانضمام للتيم...\n[C][B][FFA500]كود التيم: {team_code}", uid)
                    )

                    # محاولة الانضمام للتيم عبر الكود
                    try:
                        join_teamcode(socket_client, team_code, key, iv)
                        
                        # انتظار قصير للتأكد من الانضمام
                        sleep(2)
                        
                        clients.send(
                            self.GenResponsMsg(f"[C][B][00FF00]✅ تم الانضمام بنجاح للتيم!\n[C][B][32CD32]كود التيم: {team_code}", uid)
                        )
                        
                    except Exception as join_error:
                        print(f"Error joining team: {join_error}")
                        clients.send(
                            self.GenResponsMsg(f"[C][B][FF0000]❌ فشل في الانضمام للتيم!\n[C][B][FFFF00]تأكد من صحة الكود: {team_code}", uid)
                        )

                except Exception as e:
                    print(f"Error in @come command: {e}")
                    try:
                        clients.send(self.GenResponsMsg("[C][B][FF0000]❌ خطأ في أمر الانضمام", uid))
                    except:
                        pass
            if '1200' in data.hex()[0:4] and b'@attack' in data:
                try:
                    # --- 1. استخراج البيانات من الرسالة ---
                    split_data = re.split(rb'@attack', data)
                    command_parts = split_data[1].split(b'(')[0].decode().strip().split()

                    json_result = get_available_room(data.hex()[10:])
                    parsed_data = json.loads(json_result)
                    uid = parsed_data['5']['data']['1']['data']

                    # --- التحقق من وجود كود الفريق ---
                    if not command_parts:
                        clients.send(self.GenResponsMsg("[C][B][FF0000]الرجاء إدخال كود الفريق. مثال:\n@attack [TeamCode]", uid))
                        continue

                    team_code = command_parts[0]
                    
                    # --- إعلام المستخدم ببدء الهجوم ---
                    clients.send(
                        self.GenResponsMsg(f"[C][B][FFA500]بدء هجوم مزدوج ومكثف على {team_code}...", uid)
                    )

                    # --- 2. دمج هجوم اللاج والبدء في حلقة واحدة سريعة ---
                    start_packet = self.start_autooo()
                    leave_packet = self.leave_s()

                    # تنفيذ الهجوم المدمج لمدة 45 ثانية
                    attack_start_time = time.time()
                    while time.time() - attack_start_time < 45:
                        # انضمام
                        join_teamcode(socket_client, team_code, key, iv)
                        
                        # إرسال أمر البدء فورًا
                        socket_client.send(start_packet)
                        
                        # إرسال أمر المغادرة فورًا
                        socket_client.send(leave_packet)
                        
                        # انتظار بسيط جدًا لمنع الضغط الزائد على الشبكة
                        time.sleep(0.15)

                    # --- 3. إعلام المستخدم بانتهاء الهجوم ---
                    clients.send(
                        self.GenResponsMsg(f"[C][B][00FF00]اكتمل الهجوم المزدوج على الفريق {team_code}!", uid)
                    )

                except Exception as e:
                    print(f"An error occurred in @attack command: {e}")
                    try:
                        clients.send(self.GenResponsMsg("[C][B][FF0000]حدث خطأ أثناء تنفيذ الهجوم.", uid))
                    except:
                        pass     
                
                                               
    def parse_my_message(self, serialized_data):
        MajorLogRes = MajorLoginRes_pb2.MajorLoginRes()
        MajorLogRes.ParseFromString(serialized_data)
        
        timestamp = MajorLogRes.kts
        key = MajorLogRes.ak
        iv = MajorLogRes.aiv
        BASE64_TOKEN = MajorLogRes.token
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp, key, iv, BASE64_TOKEN

    def GET_PAYLOAD_BY_DATA(self,JWT_TOKEN , NEW_ACCESS_TOKEN,date):
        token_payload_base64 = JWT_TOKEN.split('.')[1]
        token_payload_base64 += '=' * ((4 - len(token_payload_base64) % 4) % 4)
        decoded_payload = base64.urlsafe_b64decode(token_payload_base64).decode('utf-8')
        decoded_payload = json.loads(decoded_payload)
        NEW_EXTERNAL_ID = decoded_payload['external_id']
        SIGNATURE_MD5 = decoded_payload['signature_md5']
        now = datetime.now()
        now =str(now)[:len(str(now))-7]
        formatted_time = date
        payload = bytes.fromhex("1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366")
        payload = payload.replace(b"2025-07-30 11:02:51", str(now).encode())
        payload = payload.replace(b"c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94", NEW_ACCESS_TOKEN.encode("UTF-8"))
        payload = payload.replace(b"4306245793de86da425a52caadf21eed", NEW_EXTERNAL_ID.encode("UTF-8"))
        payload = payload.replace(b"7428b253defc164018c604a1ebbfebdf", SIGNATURE_MD5.encode("UTF-8"))
        PAYLOAD = payload.hex()
        PAYLOAD = encrypt_api(PAYLOAD)
        PAYLOAD = bytes.fromhex(PAYLOAD)
        whisper_ip, whisper_port, online_ip, online_port = self.GET_LOGIN_DATA(JWT_TOKEN , PAYLOAD)
        return whisper_ip, whisper_port, online_ip, online_port
    
    def dec_to_hex(ask):
        ask_result = hex(ask)
        final_result = str(ask_result)[2:]
        if len(final_result) == 1:
            final_result = "0" + final_result
            return final_result
        else:
            return final_result
    def convert_to_hex(PAYLOAD):
        hex_payload = ''.join([f'{byte:02x}' for byte in PAYLOAD])
        return hex_payload
    def convert_to_bytes(PAYLOAD):
        payload = bytes.fromhex(PAYLOAD)
        return payload
    def GET_LOGIN_DATA(self, JWT_TOKEN, PAYLOAD):
        url = "https://clientbp.ggwhitehawk.com/GetLoginData"
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JWT_TOKEN}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'clientbp.ggwhitehawk',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                response = requests.post(url, headers=headers, data=PAYLOAD,verify=False)
                response.raise_for_status()
                x = response.content.hex()
                json_result = get_available_room(x)
                parsed_data = json.loads(json_result)
                print(parsed_data)
                
                whisper_address = parsed_data['32']['data']
                online_address = parsed_data['14']['data']
                online_ip = online_address[:len(online_address) - 6]
                whisper_ip = whisper_address[:len(whisper_address) - 6]
                online_port = int(online_address[len(online_address) - 5:])
                whisper_port = int(whisper_address[len(whisper_address) - 5:])
                return whisper_ip, whisper_port, online_ip, online_port
            
            except requests.RequestException as e:
                print(f"Request failed: {e}. Attempt {attempt + 1} of {max_retries}. Retrying...")
                attempt += 1
                time.sleep(2)

        print("Failed to get login data after multiple attempts.")
        return None, None

    def guest_token(self,uid , password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {"Host": "100067.connect.garena.com","User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 10;en;EN;)","Content-Type": "application/x-www-form-urlencoded","Accept-Encoding": "gzip, deflate, br","Connection": "close",}
        data = {"uid": f"{uid}","password": f"{password}","response_type": "token","client_type": "2","client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3","client_id": "100067",}
        response = requests.post(url, headers=headers, data=data)
        data = response.json()
        NEW_ACCESS_TOKEN = data['access_token']
        NEW_OPEN_ID = data['open_id']
        OLD_ACCESS_TOKEN = "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94"
        OLD_OPEN_ID = "4306245793de86da425a52caadf21eed"
        time.sleep(0.2)
        data = self.TOKEN_MAKER(OLD_ACCESS_TOKEN , NEW_ACCESS_TOKEN , OLD_OPEN_ID , NEW_OPEN_ID,uid)
        return(data)
        
    def TOKEN_MAKER(self,OLD_ACCESS_TOKEN , NEW_ACCESS_TOKEN , OLD_OPEN_ID , NEW_OPEN_ID,id):
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Content-Length': '928',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.ggwhitehawk.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        data = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')
        data = data.replace(OLD_OPEN_ID.encode(),NEW_OPEN_ID.encode())
        data = data.replace(OLD_ACCESS_TOKEN.encode() , NEW_ACCESS_TOKEN.encode())
        hex = data.hex()
        d = encrypt_api(data.hex())
        Final_Payload = bytes.fromhex(d)
        URL = "https://loginbp.ggwhitehawk.com/MajorLogin"

        RESPONSE = requests.post(URL, headers=headers, data=Final_Payload,verify=False)
        
        combined_timestamp, key, iv, BASE64_TOKEN = self.parse_my_message(RESPONSE.content)
        if RESPONSE.status_code == 200:
            if len(RESPONSE.text) < 10:
                return False
            whisper_ip, whisper_port, online_ip, online_port =self.GET_PAYLOAD_BY_DATA(BASE64_TOKEN,NEW_ACCESS_TOKEN,1)
            self.key = key
            self.iv = iv
            print(key, iv)
            return(BASE64_TOKEN, key, iv, combined_timestamp, whisper_ip, whisper_port, online_ip, online_port)
        else:
            return False
    
    def time_to_seconds(hours, minutes, seconds):
        return (hours * 3600) + (minutes * 60) + seconds

    def seconds_to_hex(seconds):
        return format(seconds, '04x')
    
    def extract_time_from_timestamp(timestamp):
        dt = datetime.fromtimestamp(timestamp)
        h = dt.hour
        m = dt.minute
        s = dt.second
        return h, m, s
    
    def get_tok(self):
        global g_token
        token, key, iv, Timestamp, whisper_ip, whisper_port, online_ip, online_port = self.guest_token(self.id, self.password)
        g_token = token
        print(whisper_ip, whisper_port)
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            account_id = decoded.get('account_id')
            encoded_acc = hex(account_id)[2:]
            hex_value = dec_to_hex(Timestamp)
            time_hex = hex_value
            BASE64_TOKEN_ = token.encode().hex()
            print(f"Token decoded and processed. Account ID: {account_id}")
        except Exception as e:
            print(f"Error processing token: {e}")
            return

        try:
            head = hex(len(encrypt_packet(BASE64_TOKEN_, key, iv)) // 2)[2:]
            length = len(encoded_acc)
            zeros = '00000000'

            if length == 9:
                zeros = '0000000'
            elif length == 8:
                zeros = '00000000'
            elif length == 10:
                zeros = '000000'
            elif length == 7:
                zeros = '000000000'
            else:
                print('Unexpected length encountered')
            head = f'0115{zeros}{encoded_acc}{time_hex}00000{head}'
            final_token = head + encrypt_packet(BASE64_TOKEN_, key, iv)
            print("Final token constructed successfully.")
        except Exception as e:
            print(f"Error constructing final token: {e}")
        token = final_token
        self.connect(token, 'anything', key, iv, whisper_ip, whisper_port, online_ip, online_port)
        
      
        return token, key, iv
        
with open('l9bi7e.txt', 'r') as file:
    data = json.load(file)
ids_passwords = list(data.items())

# تعريف threads هنا
all_threads = []

def run_client(id, password):
    print(f"ID: {id}, Password: {password}")
    client = FF_CLIENT(id, password)
    client.start()

max_range = 300000
num_clients = len(ids_passwords)
num_threads = 1
start = 0
end = max_range
step = (end - start) // num_threads

for i in range(num_threads):
    ids_for_thread = ids_passwords[i % num_clients]
    id, password = ids_for_thread
    thread = threading.Thread(target=lambda: run_client(id, password))
    all_threads.append(thread)
    time.sleep(3)
    thread.start()

for thread in all_threads:
    thread.join()
    
if __name__ == "__main__":
    try:
        client_thread = FF_CLIENT(id="4505619018", password="2F7B4F427F577DBC3553BA895B7C34A7A0C03A2FA5AE66E429D5CBC90800AF16")
        client_thread.start()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        restart_program()