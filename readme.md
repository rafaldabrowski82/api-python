Kod w pythonie (flask, mariadb) do testowania API
Po uruchomieniu dostępny na adresie http://localhost:5000
curl http://localhost:5000/tasks
powyższe powinno zwrócić pustą tablicę.

ADD (CREATE)

Dodaj nowe zadanie:

curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Pierwszy task!"}'


✅ Odpowiedź:
{"message":"Task added","id":1}
👉 Zapamiętaj id, będzie potrzebne dalej.





✅ READ (GET) — pobierz wszystkie
curl http://localhost:5000/tasks


Odpowiedź np.:

[
  {
    "id": 1,
    "title": "Pierwszy task!"
  }
]




✅ READ ONE (GET / ID)
curl http://localhost:5000/tasks/1





✅ UPDATE (PUT)

Zmieniamy tytuł zadania z ID=1:

curl -X PUT http://localhost:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Zaktualizowany task ✅"}'


Sprawdź ponownie:

curl http://localhost:5000/tasks/1





✅ DELETE
curl -X DELETE http://localhost:5000/tasks/1


Sprawdzamy, czy zniknął:

curl http://localhost:5000/tasks





🎯 Co właśnie ogarnąłeś?
Operacja	HTTP	Endpoint	SQL
Create	    POST	/tasks	    INSERT
Read all	GET	    /tasks	    SELECT *
Read one	GET	    /tasks/<id>	SELECT WHERE
Update	    PUT	    /tasks/<id>	UPDATE
Delete	    DELETE	/tasks/<id>	DELETE

To jest pełen CRUD ✅
Masz za sobą fundament REST API 💪

🔥 Bonus: Skrócona ściąga curl dla DevOps
Akcja	Komenda
GET	    curl URL
POST	curl -X POST -d '{json}' URL
PUT	    curl -X PUT -d '{json}' URL
DELETE	curl -X DELETE URL




GRAPHQL
⚡ 2️⃣ Testowanie GraphQL w Postmanie

Postman ma wbudowany tryb GraphQL, więc nie musisz ręcznie pisać JSON-a.

🧩 Krok po kroku
1. Wybierz nowy request:

Metoda: POST

📍 Adres wspólny dla wszystkich:
POST http://localhost:5000/graphql

📍 Nagłówki (Headers):
Content-Type: application/json

🧠 1️⃣ Pobranie wszystkich zadań

Body → raw → JSON

{
  "query": "{ allTasks { id title description status } }"
}

🧩 2️⃣ Pobranie jednego zadania po ID
{
  "query": "{ task(id: 1) { id title description status } }"
}

➕ 3️⃣ Utworzenie nowego zadania
{
  "query": "mutation { createTask(title: \"Nowe zadanie\", description: \"Opis testowy\", status: \"pending\") { id title description status } }"
}

✏️ 4️⃣ Aktualizacja istniejącego zadania
{
  "query": "mutation { updateTask(id: 1, title: \"Zmieniony tytuł\", status: \"done\") { id title description status } }"
}

❌ 5️⃣ Usunięcie zadania
{
  "query": "mutation { deleteTask(id: 1) }"
}

⚙️ Dodatkowo — przykład z parametrami dynamicznymi

Jeśli chcesz używać zmiennych (bardziej profesjonalny sposób), możesz to zrobić tak:

🔹 Body:
{
  "query": "mutation ($t: String!, $d: String!, $s: String!) { createTask(title: $t, description: $d, status: $s) { id title status } }",
  "variables": {
    "t": "Dynamiczny tytuł",
    "d": "Opis dynamiczny",
    "s": "pending"
  }
}

🔍 Podsumowanie
Cel	                 Typ	         Body (JSON)	
Pobierz wszystkie	   query	       { "query": "{ allTasks { id title } }" }	          ✅
Pobierz 1 task	     query	       { "query": "{ task(id: 1) { id title } }" }	      ✅
Dodaj nowy	         mutation	     { "query": "mutation { createTask(...) {...} }" }	✅
Zaktualizuj	         mutation	     { "query": "mutation { updateTask(...) {...} }" }	✅
Usuń	               mutation	     { "query": "mutation { deleteTask(id: 1) }" }	    ✅





