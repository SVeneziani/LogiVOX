# LogiVOX — gli occhi sui puntali, la misura a voce

Premi il pedale e ascolta la misura. Attiva AUTO e lascia che LogiVOX annunci i cambiamenti significativi quando il valore si stabilizza. Un accessorio costruito per il banco, collegato via USB senza aprire il multimetro.

Progetto di **Sergio Veneziani** per leggere ad alta voce le misure dell'OWON XDM1041 senza distogliere lo sguardo dal lavoro. Raspberry Pi Zero 2 W, collegamento USB, amplificatore MAX98357A, pedale, pulsante TALK/AUTO e UPS con distacco automatico.

Il prototipo è completato e funzionante. Questa copia è una **versione di sviluppo pubblica**: non è ancora una release pronta da costruire.

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
- Il [rapporto hardware](docs/HARDWARE-REVIEW.md) riporta i controlli superati e le verifiche prima della produzione.

## Stato e prossimi passi

- DRC PCB verificato il 4 novembre 2026: zero violazioni e zero connessioni mancanti. Anche il confronto schema–PCB è privo di segnalazioni. Verificare comunque i requisiti produttivi prima di ordinare.
- Completare istruzioni di stampa ed esportazioni STEP/STL.
- Completare e provare l'installazione su un Raspberry pulito.
- Definire la licenza software e chiarire la distribuzione delle registrazioni vocali.

Codice e test sono in `Software/`. Il server web/USB è il progetto separato [owon-xdm1041-server di Jason Antman](https://github.com/jantman/owon-xdm1041-server), non una dashboard sviluppata da zero per LogiVOX. Crediti completi nel [README inglese](README.md).

## File 3D

- [Progetto Autodesk Fusion](3D/AutodeskFusion/LogiVOX.f3d)
- [Progetto Bambu Studio](3D/BambuStudio/LogiVOX.3mf)

I file originali sono inclusi senza modifiche. Contenuto delle piastre e impostazioni di stampa da verificare nell’applicazione; dettagli in [enclosure](enclosure/README.md).

## Foto e video

[16 fotografie e un video del progetto](Foto_Video/README.md).

## Componenti acquistati

[Pedale, modulo di alimentazione e connettori utilizzati nel prototipo](docs/COMPONENTS.md).

## Licenza

I contributi originali ai file hardware e al contenitore sono distribuiti sotto **CC BY-NC-SA 4.0**: attribuzione, uso non commerciale e stessa licenza per gli adattamenti condivisi. Autorizzazioni commerciali ed eventuali royalty richiedono un accordo scritto separato con Sergio Veneziani; non sono automatiche.

Vedi [ambito ed esclusioni](LICENSE.md). Software, documentazione generale, foto/video, materiali di terzi e registrazioni vocali non sono inclusi in questa licenza dei file di progetto. Restano salvi eventuali diritti già validamente concessi con licenze precedenti.
