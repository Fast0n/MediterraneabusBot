# Your Bot token (get it from BotFather)
token = 'TOKEN'

# Message send when user 'start' the bot
start_msg = "Benvenuto su @Mediterraneabus\_Bot\n"\
            "semplice Bot Telegram per la visualizzazione degli orari della www.mediterranebus.com\n"\
            "Per cercare l'orario scrivere /orari\n\n"\
            "_Il bot è stato creato in modo non ufficiale MEDITERRANEABUS SPA. "\
            "non è respnsabile in alcun modo_"

# File with 'started' clients
client_file = "clients_id.txt"

# hours
orari = [
    ["Africo N. -farmacia", "Amendolea", "Anconi"],
    ["Antonimina", "Ardore - stazione FS", "Bagni Termali"],
    ["Belloro", "Benestare", "Bianco -piazza FS"],
    ["bivio Arena", "bivio Coop.Aspr", "bivio Monasterace"],
    ["bivio Mongiana", "bivio Moschetta", "bivio Portigliola"],
    ["bivio S.S. 112", "bivio San Lorenzo", "bivio Senoli"],
    ["bivio Staiti", "Bosco S.P.", "Bova M. -piazza FS"],
    ["Bovalino M. - piazza FS", "Bovalino p.zza Mercato", "Bovalino Sup."],
    ["Brancaleone -piazza FS", "Bruzzano Zeffirio", "Camocelli"],
    ["Canale", "Capo Spartivento -SS106", "Caraffa del B."],
    ["Careri", "Casignana", "Cassari"],
    ["Caulonia M - stazione FS", "Ceravolo", "Cittannova"],
    ["Condofuri M. -bivio stazione FS", "Condofuri Superiore", "Croceferrata"],
    ["Cutrucchi", "Fabrizia", "Ferruzzano -bivio stazione FS"],
    ["Ferruzzano S.", "Franceschella", "Gerace"],
    ["Gioiosa J. Galea", "Gioiosa J. Madamalena", "Gioiosa Jonica"],
    ["Grotteria", "Junchi", "Lacchi"],
    ["Limmara", "Locri - piazza Martiri", "Locri - piazza Tribunale Vecchio"],
    ["Locri - stazione FS", "Marina di Gioiosa J.", "Martone"],
    ["Melito P.S. -INPS", "Merici", "Mongiana"],
    ["Moschetta", "Motticella", "Nardodipace"],
    ["Natile Nuovo", "Natile V.", "Palizzi -piazza FS"],
    ["Pardesca", "Petrara", "Pizzurra"],
    ["Placanica", "Platì", "Portello"],
    ["Portigliola", "Pozzo", "Prisdarello"],
    ["Reggio Cal. Pineta Zerbi", "Reggio Calabria -C. Portanova",
        "Reggio Calabria -Porto"],
    ["Reggio Calabria -stazione FS", "REGGIO CALABRIA AEROPORTO", "Roccella J."],
    ["Rosarno", "Russellina", "S. Pasquale -SS 106"],
    ["Saline J.", "Samo", "San Carlo"],
    ["San Giovanni di Gerace", "San Luca", "Sandrechi"],
    ["Sant'Agata del B.", "Sant'Ilario dello Jonio - Stazione FS", "Scarparina"],
    ["Serra San Bruno", "Siderno - piazza Municipio", "Siderno - piazza Portosalvo"],
    ["Siderno piazza Ospedale", "Spropoli -SS 106", "Staiti "],
    ["Stazione F.S. Rosarno", "Svincolo S.G.C. Gioiosa Ionica",
        "Svincolo S.G.C. Mammola"],
    ["Timpa B.", "Tre Arie "]
]