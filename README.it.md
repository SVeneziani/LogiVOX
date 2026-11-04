# LogiVOX — una voce per il multimetro da banco

Progetto di **Sergio Veneziani** per leggere ad alta voce le misure dell'OWON XDM1041 senza distogliere lo sguardo dal lavoro. Raspberry Pi Zero 2 W, collegamento USB, amplificatore MAX98357A, pedale, pulsante TALK/AUTO e UPS con distacco automatico.

Il prototipo è completato e funzionante. Questa copia è una **bozza privata di preparazione alla pubblicazione**: non è ancora una release pronta da costruire.

## Uso

- Pedale: legge la misura alla pressione.
- TALK breve: legge al rilascio.
- TALK lungo, due secondi: attiva o disattiva AUTO, con annuncio.
- AUTO: legge la prima misura stabile e poi variazioni significative. Non ripete un valore fermo. Soglie iniziali: 1% di variazione, circa un secondo di stabilità, limiti assoluti per il rumore vicino allo zero; dettagli in [TALK-AUTO](docs/TALK-AUTO.md).
- FORCE OFF: distacco immediato hardware, distinto dallo spegnimento ordinato gestito dall'UPS.

## Correzioni importanti del prototipo

- C7 è **4,7 µF**, non 10 nF (marcatura 103). Valore e impronta definitiva vanno verificati prima di produrre una nuova scheda.
- I pin fisici **15 e 16 devono essere separati**. Assegnazione finale: pin15/BCM22 pulsante, pin16/BCM23 LED Voice.
- La prima scheda è stata modificata manualmente. Sono esclusi i vecchi Gerber per evitare di produrre la versione con errori.
- Il [rapporto hardware](docs/HARDWARE-REVIEW.md) elenca le anomalie ancora presenti nei file attuali.

## Prima della pubblicazione

- Risolvere o motivare i risultati DRC/parità e controllare le impronte.
- Aggiungere i file 3D del contenitore e una foto definitiva.
- Completare e provare l'installazione su un Raspberry pulito.
- Scegliere le licenze e chiarire la distribuzione delle registrazioni vocali.

Codice e test sono in `Software/`. Il server web/USB è il progetto separato [owon-xdm1041-server di Jason Antman](https://github.com/jantman/owon-xdm1041-server), non una dashboard sviluppata da zero per LogiVOX. Crediti completi nel [README inglese](README.md).
