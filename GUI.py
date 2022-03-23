from tkinter import Tk, Button, PhotoImage, Label, LabelFrame, W, E, N, S, Entry, END, StringVar, Scrollbar, Toplevel
from tkinter import ttk
from database_engine import DatabaseEngine


class ContactsUI:
    def __init__(self, database: DatabaseEngine):
        self.root = Tk()
        self.root.title('Contacts List App')
        self.db = database
        self.create_gui()

        self.root.mainloop()

    def create_gui(self):
        self.create_icon()
        self.create_labelframe()
        self.create_message_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_records()

    def create_icon(self):
        photo = PhotoImage(file='icons/logo.png')
        label = Label(image=photo)
        label.image = photo
        label.grid(row=0, column=0)

    def create_labelframe(self):
        labelframe = LabelFrame(self.root, text='Create New Contact')
        labelframe.grid(row=0, column=1, padx=8, pady=8, sticky='ew')

        Label(labelframe, text='Name:').grid(row=1, column=1, sticky=W, pady=2, padx=15)
        self.namefield = Entry(labelframe)
        self.namefield.grid(row=1, column=2, sticky=W, padx=5, pady=2)

        Label(labelframe, text='Email:').grid(row=2, column=1, sticky=W, pady=2, padx=15)
        self.emailfield = Entry(labelframe)
        self.emailfield.grid(row=2, column=2, sticky=W, padx=5, pady=2)

        Label(labelframe, text='Number:').grid(row=3, column=1, sticky=W, pady=2, padx=15)
        self.numberfield = Entry(labelframe)
        self.numberfield.grid(row=3, column=2, sticky=W, padx=5, pady=2)

        Button(labelframe, text='Add Contact',
               command=self.add_new_contact).grid(row=4, column=2, sticky=E, padx=5, pady=5)

    def create_message_area(self):
        self.message = Label(text='')
        self.message.grid(row=3, column=1, sticky=W)

    def create_tree_view(self):
        self.tree = ttk.Treeview(height=10, columns=('email', 'number'))
        self.tree.grid(row=6, column=0, columnspan=3, padx=5)
        self.tree.heading('#0', text='Name', anchor=W)
        self.tree.heading('email', text='Email Address', anchor=W)
        self.tree.heading('number', text='Contact Number', anchor=W)

    def create_scrollbar(self):
        self.scrollbar = Scrollbar(orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=6, column=3, rowspan=2, sticky='sn')

    def create_bottom_buttons(self):
        Button(text='Delete Selected', command=self.delete_record).grid(row=8, column=0, sticky=W, pady=10, padx=20)
        Button(text='Modify Selected',
               command=self.open_modify_window).grid(row=8, column=1, sticky=W, pady=10, padx=20)

    def new_contact_validation(self):
        return len(self.namefield.get()) != 0 and len(self.emailfield.get()) != 0 and len(self.numberfield.get()) != 0

    def view_records(self):
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)

        query = 'SELECT * FROM contacts_list ORDER BY name desc'
        contact_entries = self.db.execute_query(query)
        for row in contact_entries:
            self.tree.insert('', 0, text=row[1], values=(row[2], row[3]))

    def add_new_contact(self):
        if self.new_contact_validation():
            query = 'INSERT INTO contacts_list VALUES(NULL, ?, ?, ?)'
            parameters = (self.namefield.get(), self.emailfield.get(), self.numberfield.get())

            self.db.execute_query(query, parameters)
            self.message['text'] = f'New contact {self.namefield.get()} added'

            self.namefield.delete(0, END)
            self.emailfield.delete(0, END)
            self.numberfield.delete(0, END)
        else:
            self.message['text'] = 'Name, Email or Number cannot be blank'

        self.view_records()

    def delete_record(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected'
            return
        else:
            name = self.tree.item(self.tree.selection())['text']
            query = 'DELETE FROM contacts_list WHERE name = ?'
            self.db.execute_query(query, (name,))
            self.message['text'] = f'Contact for {name} deleted'
            self.view_records()

    def open_modify_window(self):
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected'
            return
        else:
            name = self.tree.item(self.tree.selection())['text']
            old_email = self.tree.item(self.tree.selection())['values'][0]
            old_number = self.tree.item(self.tree.selection())['values'][1]

            self.transient = Toplevel()
            self.transient.title('Update Contact')

            Label(self.transient, text='Name:').grid(row=0, column=1)
            Entry(self.transient, textvariable=StringVar(
                self.transient, value=name), state='readonly').grid(row=0, column=2)

            Label(self.transient, text='Old/New Number:').grid(row=1, column=1)
            Entry(self.transient, textvariable=StringVar(
                self.transient, value=old_number), state='readonly').grid(row=1, column=2)

            # Label(self.transient, text='New Phone Number:').grid(row=2, column=1)
            new_number_entry = Entry(self.transient)
            new_number_entry.grid(row=1, column=3)

            Label(self.transient, text='Old/New Email:').grid(row=2, column=1)
            Entry(self.transient, textvariable=StringVar(
                self.transient, value=old_email), state='readonly').grid(row=2, column=2)

            # Label(self.transient, text='New Email:').grid(row=4, column=1)
            new_email_entry = Entry(self.transient)
            new_email_entry.grid(row=2, column=3)

            Button(self.transient, text='Update Contact',
                   command=lambda: self.update_record(
                       (new_number_entry, old_number), (new_email_entry, old_email), name)
                   ).grid(row=3, column=3, sticky=E)

            self.transient.mainloop()

    def update_record(self, phone, email, name):
        if len(phone[0].get()) == 0:
            new_phone = phone[1]
        else:
            new_phone = phone[0].get()

        if len(email[0].get()) == 0:
            new_email = email[1]
        else:
            new_email = email[0].get()

        query = 'UPDATE contacts_list SET number=?, email=? WHERE name=?'
        parameters = (new_phone, new_email, name)
        self.db.execute_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = f'Contact {name} updated'
        self.view_records()


if __name__ == '__main__':
    db = DatabaseEngine('contacts.db')
    application = ContactsUI(db)

