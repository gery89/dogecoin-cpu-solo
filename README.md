# Dogecoin cpu solo
Dogecoin Solo CPU Mining

Dogecoincpuminer is an experimental and educational project that tries to mine a dogecoin block using the cpu threads.

(Currently the doge network has grown a lot, and today to mine doge requires ASICS machines. So it is practically impossible to mine a block with a cpu)

Requirements:
  - Dogecoin core wallet with rpc. Create dogecoin.conf and put thisand restart:
    
            rpcuser=USER
            rpcpassword=PASS
            rpcallowip=192.168.1.131
            rpcbind=192.168.1.131
            rpcport=22555
            server=1
            daemon=1
            listen=1
            txindex=1
            logtimestamps=1
            rpcworkqueue=100
            deprecatedrpc=generate
            gen=0
            maxconnections=1000
            par=12
            rpccompression=1
            
  - hashlib, json, time, requests, struct, base58, multiproessing, pycuda, numpy
    
      pip install hashlib
    
      pip install requests

  Open dogecoincpu.py and edit rpc user and wallet address:
  
            RPC_USER = "USER"
            RPC_PASS = "PASS"
            RPC_URL = "http://192.168.1.131:22555"
            DOGE_PAYOUT_ADDRESS = "D689FQb1NfbPb6PVH5zMKhmWM7oe8qGomx"
    
      ...


  
