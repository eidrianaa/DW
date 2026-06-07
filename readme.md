# Acme Financial Data Warehouse

Această configurație rulează întregul ecosistem Big Data (FastAPI, Next.js, Cassandra și Apache Spark) complet izolat, folosind pachete gata configurate. Nu trebuie să instalezi Java sau baze de date pe Mac-ul tău.

 Cerințe minime
* Docker Desktop instalat și pornit.
* Git pentru gestionarea proiectului.

Cum se instalează și pornește aplicația

Deschide terminalul direct în folderul principal al proiectului (acolo unde vezi folderele backend și frontend la un loc) și rulează:

Pasul 1: Construiește și pornește containerele
docker compose up --build -d
(Această comandă va descărca imaginile de Cassandra și Spark, va instala pachetele de Python/Node și va porni totul în fundal. Prima rulare poate dura câteva minute).

Pasul 2: Creează spațiul de stocare în Cassandra (O singură dată)
Pentru că baza de date din Docker pornește complet goală, trebuie să rulăm o singură comandă care să creeze structura proiectului:
docker compose exec cassandra cqlsh -e "CREATE KEYSPACE acme_dw WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};"

Gata! În acest moment totul este activ. Deschide browserul la adresa:
http://localhost:3000

💻 Cum se lucrează în aplicație (Fluxul pentru prezentare)
Urmează acești pași direct în interfața grafică din browser pentru a popula proiectul cu date:

Pasul 1: Descarcă datele (Data Ingestion)
1. Mergi în meniul din stânga la iconița cu o săgeată în sus (Data Ingestion).
2. În căsuța Ticker Symbols, scrie: AAPL, MSFT, TSLA, GOOGL, NVDA.
3. Alege perioada 6 Months și apasă pe butonul Start Ingestion.
* Ce se întâmplă: Serverul FastAPI va descărca sute de prețuri reale de pe internet și le va trimite direct în containerul izolat de Cassandra.

Pasul 2: Verifică ecranul principal (Home)
1. Mergi la prima iconiță din stânga (Home).
2. Numărul de TOTAL RECORDS nu mai este zero, ci va afișa volumul de date stocate, iar graficele de pe ecran vor prinde viață.

Pasul 3: Rulează calculele Big Data (Analytics & Predictions)
1. Mergi la iconița de Analytics (graficele cu linii din meniu).
2. Apasă pe butonul roz Run Aggregation Job sau Run Prediction.
* Ce se întâmplă: Containerul cu Apache Spark se va trezi instant, va citi datele brute din Cassandra, le va procesa prin algoritmi de map-reduce / modele de ML și va trimite rezultatele finale înapoi în interfață sub formă de grafice și tabele cu medii financiare.

Comenzi utile pentru gestionare

Oprește aplicația (fără să ștergi datele):
docker compose stop

Repornește aplicația rapid:
docker compose start

Șterge tot și curăță memoria (reset total):
docker compose down -v
