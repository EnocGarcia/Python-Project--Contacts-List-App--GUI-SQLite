from database_engine import DatabaseEngine
from GUI import ContactsUI

db = DatabaseEngine('contacts.db')
application = ContactsUI(db)
