import json
import hashlib
import time
import requests
import struct
import base58
import multiprocessing
import os
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import numpy as np




# Configuración RPC de Dogecoin Core
RPC_USER = "USER"
RPC_PASS = "PASS"
RPC_URL = "http://192.168.1.131:22555"
DOGE_PAYOUT_ADDRESS = "D689FQb1NfbPb6PVH5zMKhmWM7oe8qGomx"  # 🤑 Reemplaza con tu dirección Dogecoin

def rpc_request(method, params=[]):
    headers = {"content-type": "application/json"}
    data = json.dumps({"jsonrpc": "1.0", "id": "miner", "method": method, "params": params})
    response = requests.post(RPC_URL, headers=headers, data=data, auth=(RPC_USER, RPC_PASS))
    return response.json()

def sha256d(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
    
    
    return result_hash
def base58_to_hash160(address):
    decoded = base58.b58decode_check(address)
    return decoded[1:]  # Quita el prefijo de versión

def create_coinbase_tx(coinbase_value):
    version = struct.pack("<L", 1)
    input_count = b'\x01'
    prev_tx = b'\x00' * 32  # TXID vacío porque es coinbase
    prev_index = struct.pack("<L", 0xFFFFFFFF)  # Índice de entrada para coinbase
    script_sig = b'\x04' + b'mine'  # Script de firma (puede variar dependiendo de la implementación)
    script_sig_length = struct.pack("B", len(script_sig))  # Longitud del script de firma
    sequence = struct.pack("<L", 0xFFFFFFFF)  # Secuencia (valor máximo para coinbase)
    output_count = b'\x01'
    reward = struct.pack("<Q", coinbase_value)  # Valor de la recompensa (8 bytes)
    hash160 = base58_to_hash160(DOGE_PAYOUT_ADDRESS)
    script_pubkey = b'\x76\xa9\x14' + hash160 + b'\x88\xac'
    script_pubkey_length = struct.pack("B", len(script_pubkey))  # Longitud del script de salida
    output = reward + script_pubkey_length + script_pubkey  # Salida completa
    locktime = struct.pack("<L", 0)  # Locktime (sin restricciones de tiempo)
    coinbase_tx = (version + input_count + prev_tx + prev_index + 
                   script_sig_length + script_sig + sequence + 
                   output_count + output + locktime)
    return coinbase_tx.hex()

def calculate_merkle_root(transactions):
    transaction_hashes = [bytes.fromhex(tx['txid'])[::-1] for tx in transactions]
    while len(transaction_hashes) > 1:
        if len(transaction_hashes) % 2 != 0:
            transaction_hashes.append(transaction_hashes[-1])  # Duplicar último hash si es impar
        new_level = []
        for i in range(0, len(transaction_hashes), 2):
            combined = transaction_hashes[i] + transaction_hashes[i + 1]
            new_level.append(sha256d(combined))
        transaction_hashes = new_level
    return transaction_hashes[0][::-1].hex()

def mine_block(nonce_start, nonce_end, queue, thread_id):
    contador_local = 0
    inicio = time.time()
    while True:
        block_template = rpc_request("getblocktemplate")
        if "result" not in block_template:
            print("[-] Error al obtener el template:", block_template)
            return
        block = block_template["result"]
        merkle_root = calculate_merkle_root(block["transactions"])
        coinbase_tx = create_coinbase_tx(block["coinbasevalue"])
        version = block["version"].to_bytes(4, "little")
        prev_block = bytes.fromhex(block["previousblockhash"])[::-1]
        bits = bytes.fromhex(block["bits"])
        target = int(block["target"], 16)
        nonce = nonce_start
        timestamp = int(time.time()).to_bytes(4, "little")
        while nonce < nonce_end:
            nonce_bytes = nonce.to_bytes(4, "little")
            block_header = version + prev_block + bytes.fromhex(merkle_root) + timestamp + bits + nonce_bytes
            block_hash = sha256d(block_header)[::-1].hex()
            contador_local += 1
            if int(block_hash, 16) < target:
                print(f"[✓] ¡Bloque encontrado! Hash: {block_hash}, Nonce: {nonce}")
                submit_block(block_header.hex(), coinbase_tx, block["transactions"])
                break
            if time.time() - inicio >= 10: 
                queue.put(contador_local)
                contador_local = 0
                inicio = time.time()
            nonce += 1

def submit_block(block_header_hex, coinbase_tx_hex, transactions):
    full_block = block_header_hex + coinbase_tx_hex  
    for tx in transactions:
        full_block += tx['data'] 

    result = rpc_request("submitblock", [full_block])
    
    if result is None:
        print("[✓] Bloque enviado correctamente")
    else:
        print("[✗] Error al enviar el bloque:", result)

def mostrar_estadisticas(queue, tiempo_inicio):
    contador_global = 0
    while True:
        time.sleep(10)  
        operaciones_intervalo = 0
        while not queue.empty():
            operaciones_intervalo += queue.get()
        contador_global += operaciones_intervalo
        tiempo_transcurrido = time.time() - tiempo_inicio
        gh_s = operaciones_intervalo / 10  
        os.system('cls' if os.name == 'nt' else 'clear') 
        gh_s = gh_s / 1_000_000_000 
        print(f"Estadísticas de Minería:")
        print(f"======================")
        print(f"Operaciones/S: {gh_s:.8f} GHS/s")
        print(f"Total de operaciones: {contador_global}")
        print(f"Tiempo: {tiempo_transcurrido / 60:.2f} minutos")

def start_mining(threads):
    total_nonces = 2**32  # Rango de nonces ajustado a 32 bits (Dogecoin usa 4 bytes)
    nonces_per_thread = total_nonces // threads
    queue = multiprocessing.Queue()
    procesos = []
    tiempo_inicio = time.time()
    proceso_estadisticas = multiprocessing.Process(target=mostrar_estadisticas, args=(queue, tiempo_inicio))
    proceso_estadisticas.start()
    procesos.append(proceso_estadisticas)

    for i in range(threads):
        nonce_start = i * nonces_per_thread
        nonce_end = (i + 1) * nonces_per_thread
        proceso = multiprocessing.Process(target=mine_block, args=(nonce_start, nonce_end, queue, i))
        proceso.start()
        procesos.append(proceso)

    for proceso in procesos:
        proceso.join()

if __name__ == "__main__":
    threads = os.cpu_count()
    start_mining(threads)  # Puedes cambiar el número de hilos de minería
