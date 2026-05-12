import json, time, random, datetime, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# المفاتيح الثابتة
Key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
Iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# دوال التشفير الأساسية
def EnC_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return cipher.encrypt(pad(bytes.fromhex(HeX), AES.block_size)).hex()
    
def DEc_AEs(HeX):
    cipher = AES.new(Key, AES.MODE_CBC, Iv)
    return unpad(cipher.decrypt(bytes.fromhex(HeX)), AES.block_size).hex()
    
def EnC_PacKeT(HeX, K, V): 
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()
    
def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

# دوال التحويل
def EnC_Uid(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def DEc_Uid(H):
    n = s = 0
    for b in bytes.fromhex(H):
        n |= (b & 0x7F) << s
        if not b & 0x80: break
        s += 7
    return n

def EnC_Vr(N):
    if N < 0: return ''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def DecodE_HeX(H):
    R = hex(H) 
    F = str(R)[2:]
    if len(F) == 1: 
        F = "0" + F
        return F
    else: 
        return F

# دوال البروتوباف
def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))           
    return packet

def GeneRaTePk(Pk, N, K, V):
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

# دوال المساعدة
def ArA_CoLor():
    Tp = ["32CD32", "00BFFF", "00FA9A", "90EE90", "FF4500", "FF6347", "FF69B4", 
          "FF8C00", "FF6347", "FFD700", "FFDAB9", "F0F0F0", "F0E68C", "D3D3D3", 
          "A9A9A9", "D2691E", "CD853F", "BC8F8F", "6A5ACD", "483D8B", "4682B4", 
          "9370DB", "C71585", "FF8C00", "FFA07A"]
    return random.choice(Tp)
    
def xBunnEr():
    bN = [902000306, 902000305, 902000003, 902000016, 902000017, 902000019, 
          902000020, 902000021, 902000023, 902000070, 902000087, 902000108, 
          902000011, 902049020, 902049018, 902049017, 902049016, 902049015, 
          902049003, 902033016, 902033017, 902033018, 902048018, 902000306, 902000305]
    return random.choice(bN)

def xMsGFixinG(n):
    return '🗿'.join(str(n)[i:i + 3] for i in range(0, len(str(n)), 3))

# دوال الرسائل
def xSEndMsg(Msg, Tp, Tp2, id, K, V):
    fields = {
        1: id, 2: Tp2, 3: Tp, 4: Msg, 5: 1735129800, 7: 2, 
        9: {
            1: "xBesTo - C4", 2: xBunnEr(), 3: 901048018, 4: 330, 
            5: 909034009, 8: "xBesTo - C4", 10: 1, 11: 1, 
            14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
        }, 
        10: "en", 13: {2: 1, 3: 1}, 14: {}
    }
    Pk = str(CrEaTe_ProTo(fields).hex())
    Pk = "080112" + EnC_Uid(len(Pk) // 2, 'Uid') + Pk
    return GeneRaTePk(str(Pk), '1215', K, V)

def xSendTeamMsg(msg, idT, K, V):
    fields = {
        1: 1,
        2: {
            1: 12404281032,
            2: idT,
            4: msg,
            7: 2,
            10: "fr",
            9: {
                1: "C4 TEAM",
                2: xBunnEr(),
                4: 330,
                5: 827001005,
                8: "C4 TEAM",
                10: 1,
                11: 1,
                12: {1: 2},
                14: {1: 1158053040, 2: 8, 3: "\u0010\u0015\b\n\u000b\u0015\f\u000f\u0011\u0004\u0007\u0002\u0003\r\u000e\u0012\u0001\u0005\u0006"}
            },
            13: {1: 2, 2: 1},
            14: {}
        }
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '1215', K, V)

# دوال المجموعات
def GenJoinSquadsPacket(code, key, iv):
    fields = {
        1: 4,
        2: {
            4: bytes.fromhex("01090a0b121920"),
            5: str(code),
            6: 6,
            8: 1,
            9: {
                2: 800,
                6: 11,
                8: "1.111.1",
                9: 5,
                10: 1
            }
        }
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)

def Auth_Chat(idT, sq, K, V):
    fields = {
        1: 3,
        2: {
            1: idT,
            3: "fr",
            4: sq
        }
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '1215', K, V)

def ExiT(id, K, V):
    fields = {
        1: 7,
        2: {
            1: int(11037044965)
        }
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)

# دوال التحقق
def ChEck_Commande(id):
    return "<" not in id and ">" not in id and "[" not in id and "]" not in id

def ChEck_The_Uid(uid):
    """دالة التحقق من UID - دائماً ترجع True للبوت"""
    return True

# دوال إدارة الملفات
def load_blacklist():
    try:
        with open('blacklist.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except:
        return []

def load_approve():
    try:
        with open('approved.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except:
        return []

# دوال الحدود
def L_DaTa():
    load = lambda f: json.load(open(f)) if os.path.exists(f) else {}
    return map(load, ["BesTo_CLan_LiKes.json", "BesTo_RemaininG_LiKes.json", "BesTo_RemaininG_Room.json"])

like_data_clan, like_data, room_data = L_DaTa()

def ChEck_Limit(Uid, STaTus):
    data, max_use, file = (like_data, 10, "BesTo_RemaininG_LiKes.json") if STaTus == "like" else (room_data, 10, "BesTo_RemaininG_Room.json")
    t, limit = time.time(), 86400
    u = data.get(str(Uid), {"count": 0, "start_time": t})    
    if t - u["start_time"] >= limit:
        u = {"count": 0, "start_time": t}
    if u["count"] < max_use:
        u["count"] += 1
        data[str(Uid)] = u
        json.dump(data, open(file, "w"))
        return f"{max_use - u['count']}", datetime.fromtimestamp(u["start_time"] + limit).strftime("%I:%M %p - %d/%m/%y")
    return False, datetime.fromtimestamp(u["start_time"] + limit).strftime("%I:%M %p - %d/%m/%y")