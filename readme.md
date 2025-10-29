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
