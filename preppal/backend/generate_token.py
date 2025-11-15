import time
from agora_token_builder import RtcTokenBuilder, Role_Publisher

appID = "be55fa5694ef4d8fa813d4578ce246b1"
appCertificate = "0800aaa27ed84351b53b1af4441034e0"

channelName = "preppl_channel"
uid = 1  # browser user ID (must be NON-zero if agent uses 0)
expire_seconds = 3600

current_ts = int(time.time())
privilege_expire_ts = current_ts + expire_seconds

token = RtcTokenBuilder.buildTokenWithUid(
    appID,
    appCertificate,
    channelName,
    uid,
    Role_Publisher,
    privilege_expire_ts,
)

print("\nRTC CLIENT TOKEN:\n")
print(token)
print("\nPaste into .env as:\nAGORA_TEMP_CLIENT_TOKEN=", token)
