# Dogecoin cpu solo
Dogecoin Solo CPU Mining

Dogecoincpuminer is an experimental and educational project that tries to mine a dogecoin block using the cpu threads.

(Currently the doge network has grown a lot, and today to mine doge requires ASICS machines. So it is practically impossible to mine a block with a cpu)

Requirements:
  -Dogecoin core wallet with rpc.
  
    Create dogecoin.conf and put this:
    
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
            maxconnections=100000
            par=12
            rpccompression=1
      Restart dogecoin core wallet
  - hashlib, json, time, requests, struct, base58, multiproessing, pycuda, numpy
      pip install hashlib
      pip install requests
      ...


  
