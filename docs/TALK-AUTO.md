# TALK/AUTO — 3 novembre 2026

Il servizio  esistente `logivox-pedal` gestisce entrambi gli ingressi. Pressione breve SW1: lettura al rilascio. Pressione lunga di due secondi: abilita/disabilita AUTO con annuncio. Un pulsante premuto all'avvio deve prima essere rilasciato. Il pedale legge alla pressione e non cambia AUTO. Al riavvio AUTO è sempre spento.

AUTO acquisisce al massimo ogni 250 ms quando non sta parlando. Richiede almeno tre campioni distinti in una finestra di almeno un secondo. Oscillazione ammessa: massimo tra 0,2% del valore e soglia assoluta. Annuncia inizialmente la prima misura stabile, poi differenze di almeno 1% rispetto all'ultima pronunciata, oppure la soglia assoluta se maggiore. Nessuna ripetizione periodica di valori invariati. Tre secondi minimi dalla fine della precedente lettura. Un andamento continuamente instabile non viene annunciato: Talk/pedale consentono comunque la lettura istantanea.

Soglie assolute: tensione 1 mV, corrente 1 µA, resistenza 1 Ω, capacità 1 nF, frequenza 0,1 Hz, temperatura 0,1 °C. Sono scelte iniziali per il filtro vocale, non specifiche di accuratezza del multimetro. Parametri in `bin/logivox_auto.py`.

Cambio funzione/unità/stato fuori scala riavvia la stabilizzazione. Fuori scala viene pronunciato una volta finché lo stato non cambia. Il confronto usa anche `mode` se presente nell'API; non può distinguere modalità che il server non espone. Timestamp duplicati non contano come nuovi campioni; dati vecchi oltre tre secondi non vengono pronunciati.

Lettura HTTP e audio girano in un thread separato dalla scansione dei pulsanti. Una frase già iniziata termina normalmente; AUTO disattivato impedisce le successive. Le richieste manuali ravvicinate vengono accorpate a una sola richiesta pendente. I WAV di conferma sono `audio_it/auto_on.wav` e `auto_off.wav`. Codice di UPS/Force Off non modificato.

Verifica: 25 test locali passati, inclusi stabilizzazione, variazioni, rumore, rampa, cambio funzione, fuori scala, dati vecchi, pausa minima, pressione breve/lunga e rimbalzi. Collaudo finale TALK/AUTO sull'hardware da registrare dopo installazione.

Installazione eseguita su <raspberry-ip>: servizio avviato regolarmente, checksum dei tre moduli identici alla copia locale. Backup remoto `/home/sadmin/LogiVOX/backups/talk-auto-20261103-221406/`. Collaudo pulsante/LED dello scambio pin riuscito; prova funzionale AUTO richiesta all'utente.

## Collaudo finale confermato — 3 novembre 2026

Il funzionamento della prova completa richiesta: pressione breve per lettura, pressione lunga per attivazione AUTO con annuncio, prova di misura ferma e variata, pressione lunga per disattivazione con annuncio. Confermati anche LED Voice sul pin fisico 16 / BCM23 e pulsante sul pin fisico 15 / BCM22
