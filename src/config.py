"""
Config
central contact point for configuring variable content
"""


class general:
    group_id = 212



class mqtt:

    # standard-connection
    domain = "mothership.inf.tu-dresden.de"
    pw = '7U8CrBTFe3'
    encrypted_port = 8883
    unencrypted_port = 1883
    websocket_port = 9002

    #quality of service QoS
    #The message reaches the recipients at least once
    qos_level = 1




