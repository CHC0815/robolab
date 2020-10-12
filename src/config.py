"""
Config
ALle häufig verwendeten Werte, Strings ect.
Zentrale Anlaufstelle zum konfigurieren variabler Inhalte
"""




class motor_settings:



class general:
    group_id = 212



class mqtt:

    # Standard-Verbindung
    url = "mothership.inf.tu-dresden.de"
    pw = 1 #TODO
    encrypted_port = 8883
    unencrypted_port = 1883
    websocket_port = 9002

    #Quality of Service QoS
    #Die Nachricht erreicht die Empfänger mindestens einmal
    qos_level = 1


