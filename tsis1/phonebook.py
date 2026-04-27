from connect import connect
import csv
import json



def add_contact():
    conn = connect()
    cur = conn.cursor()

    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    
    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    g = cur.fetchone()

    if g:
        gid = g[0]
    else:
        cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group,))
        gid = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s,%s,%s,%s)
    """, (name, email, birthday, gid))

    conn.commit()
    conn.close()
    print("Contact added")



def add_phone():
    conn = connect()
    cur = conn.cursor()

    name = input("Contact name: ")
    phone = input("Phone: ")
    ptype = input("Type (home/work/mobile): ")

    cur.execute("""
        SELECT id FROM contacts WHERE name=%s
    """, (name,))

    c = cur.fetchone()
    if not c:
        print("Contact not found")
        conn.close()
        return

    cid = c[0]

    cur.execute("""
        INSERT INTO phones(contact_id, phone, type)
        VALUES (%s,%s,%s)
    """, (cid, phone, ptype))

    conn.commit()
    conn.close()
    print("Phone added")



def search():
    conn = connect()
    cur = conn.cursor()

    q = input("Search: ")

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.name ILIKE %s
           OR c.email ILIKE %s
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()

    if not rows:
        print("No results")
    else:
        for r in rows:
         name = r[0]
         email = r[1]
         birthday = r[2].strftime("%Y-%m-%d") if r[2] else None
         group = r[3]

    print(name, email, birthday, group)

    conn.close()



def filter_group():
    conn = connect()
    cur = conn.cursor()

    g = input("Group: ")

    cur.execute("""
        SELECT c.name, c.email
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name=%s
    """, (g,))

    rows = cur.fetchall()

    if not rows:
        print("No results")
    else:
        for r in rows:
            print(r)

    conn.close()



def sort_contacts():
    conn = connect()
    cur = conn.cursor()

    field = input("Sort by (name/birthday/created_at): ")

    if field not in ["name", "birthday", "created_at"]:
        print("Invalid field")
        return

    cur.execute(f"""
        SELECT name, email, birthday
        FROM contacts
        ORDER BY {field}
    """)

    for r in cur.fetchall():
        print(r)

    conn.close()



def export_json():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
    """)

    rows = cur.fetchall()

    data = []
    for r in rows:
        data.append({
            "name": r[0],
            "email": r[1],
            "birthday": str(r[2]) if r[2] else None,
            "group": r[3]
        })

    with open("contacts.json", "w") as f:
        json.dump(data, f, indent=4)

    conn.close()
    print("Export done")



def import_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row["name"]
            phone = row["phone"]
            email = row["email"]
            birthday = row["birthday"]
            group = row["group"]
            ptype = row["phone_type"]


            cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
            g = cur.fetchone()

            if g:
                gid = g[0]
            else:
                cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group,))
                gid = cur.fetchone()[0]


            cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
            c = cur.fetchone()

            if c:
                cid = c[0]
            else:
                cur.execute("""
                    INSERT INTO contacts(name,email,birthday,group_id)
                    VALUES (%s,%s,%s,%s)
                    RETURNING id
                """, (name, email, birthday, gid))
                cid = cur.fetchone()[0]

            
            cur.execute("""
                INSERT INTO phones(contact_id, phone, type)
                VALUES (%s,%s,%s)
            """, (cid, phone, ptype))

    conn.commit()
    conn.close()
    print("CSV imported DONE")



def menu():
    while True:
        print("\n PHONEBOOK ")
        print("1 Add contact")
        print("2 Add phone")
        print("3 Search")
        print("4 Filter group")
        print("5 Sort")
        print("6 Export JSON")
        print("7 Import CSV")
        print("0 Exit")

        c = input("Choose: ")

        if c == "1":
            add_contact()
        elif c == "2":
            add_phone()
        elif c == "3":
            search()
        elif c == "4":
            filter_group()
        elif c == "5":
            sort_contacts()
        elif c == "6":
            export_json()
        elif c == "7":
            import_csv()
        elif c == "0":
            break


menu()